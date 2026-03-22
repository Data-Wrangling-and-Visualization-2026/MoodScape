from apscheduler.schedulers.background import BackgroundScheduler


class SchedulerService:

    def __init__(self):
        """Create background scheduler used for periodic parsing jobs."""
        self.scheduler = BackgroundScheduler()

    def add_job(self, func, seconds: int):
        """Register recurring interval job in minutes."""
        self.scheduler.add_job(func, "interval", seconds=seconds)

    def start(self):
        """Start scheduler loop."""
        self.scheduler.start()

    def stop(self):
        """Stop scheduler loop if running."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
