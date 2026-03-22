import requests
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "http://localhost:8002/analyze"
CSV_FILE = "processed_tracks.csv"


def safe_int(value, default=0):
    """Безопасное преобразование в int"""
    try:
        if value is None or value == '':
            return default
        return int(float(value))  # Сначала преобразуем в float, потом в int
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Безопасное преобразование в float"""
    try:
        if value is None or value == '':
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_str(value, default=''):
    """Безопасное преобразование в строку"""
    if value is None:
        return default
    return str(value).strip()


def read_tracks_from_csv(file_path):
    """Читает треки из CSV файла"""
    tracks = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Пропускаем строки без текста
            lyrics = safe_str(row.get('lyrics', ''))
            if not lyrics:
                continue
            
            # Безопасно получаем loudness и делаем положительным
            loudness = safe_float(row.get('loudness', 10.0))
            if loudness < 0:
                loudness = abs(loudness)
            if loudness == 0:
                loudness = 10.0
            
            track = {
                "id": safe_int(row.get('id'), 0),
                "track_id": safe_int(row.get('track_id'), 0),
                "lyrics": lyrics,
                "title": safe_str(row.get('title', 'Unknown')),
                "main_artist": safe_str(row.get('main_artist', 'Unknown')),
                "artists": safe_str(row.get('artists', 'Unknown')),
                "genre": safe_str(row.get('genre', 'Unknown')),
                "album": safe_str(row.get('album', 'Unknown')),
                "year": safe_int(row.get('year'), 2024),
                "duration_ms": safe_int(row.get('duration_ms'), 180000),
                "mode": safe_int(row.get('mode'), 1),
                "tempo": safe_float(row.get('tempo'), 120.0),
                "energy": safe_float(row.get('energy'), 0.5),
                "valence": safe_float(row.get('valence'), 0.5),
                "loudness": loudness,
                "speechiness": safe_float(row.get('speechiness'), 0.5),
                "acousticness": safe_float(row.get('acousticness'), 0.5),
                "danceability": safe_float(row.get('danceability'), 0.5),
                "instrumentalness": safe_float(row.get('instrumentalness'), 0.0)
            }
            tracks.append(track)
    
    return tracks


def send_track(track_data):
    """Отправить один трек"""
    try:
        response = requests.post(URL, json=track_data, timeout=30)
        return {
            "id": track_data["id"],
            "title": track_data["title"],
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }
    except Exception as e:
        return {
            "id": track_data["id"],
            "title": track_data["title"],
            "success": False,
            "error": str(e)
        }


def check_queue_status():
    """Проверить статус очереди"""
    try:
        response = requests.get("http://localhost:8002/queue/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"\n📊 Статус очереди:")
            print(f"   Размер очереди: {status['queue_size']}")
            print(f"   Pipeline запущен: {status['is_running']}")
            return status
        else:
            print(f"⚠️ Ошибка получения статуса: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Не удалось получить статус очереди: {e}")
        return None


# Основная логика
print("📂 Чтение CSV файла...")
tracks = read_tracks_from_csv(CSV_FILE)

if not tracks:
    print("❌ Не найдено треков для отправки")
    exit()

print(f"✅ Загружено {len(tracks)} треков\n")

# Показываем первые 5 треков для проверки
print("📋 Первые 5 треков:")
for i, track in enumerate(tracks[:5], 1):
    print(f"   {i}. ID: {track['id']}, Название: {track['title']}, Автор: {track['main_artist']}")

if len(tracks) > 5:
    print(f"   ... и еще {len(tracks) - 5} треков\n")

# Спрашиваем подтверждение
confirm = input("🚀 Начать отправку? (y/n): ").strip().lower()
if confirm != 'y':
    print("Отменено")
    exit()

# Отправка треков
print("\n🚀 Начинаем отправку...")
successful = 0
failed = 0

for i, track in enumerate(tracks, 1):
    print(f"[{i}/{len(tracks)}] Отправка: {track['title']} ({track['main_artist']})")
    result = send_track(track)
    
    if result["success"]:
        successful += 1
        print(f"   ✅ Успешно (статус: {result['status_code']})")
        if result.get('response'):
            response_data = result['response']
            if isinstance(response_data, dict):
                print(f"   📝 Ответ: {response_data.get('status', 'unknown')}")
    else:
        failed += 1
        print(f"   ❌ Ошибка: {result.get('error', 'Unknown')}")
    
    # Небольшая задержка между запросами
    if i < len(tracks):
        time.sleep(0.5)

# Итоги
print("\n" + "=" * 50)
print(f"✅ Готово!")
print(f"   Успешно: {successful}")
print(f"   Ошибок: {failed}")
print("=" * 50)

# Проверка очереди
print("\n⏳ Проверяем статус очереди...")
time.sleep(2)
check_queue_status()