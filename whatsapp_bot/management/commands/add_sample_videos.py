from django.core.management.base import BaseCommand
from whatsapp_bot.models import WelcomeVideo


class Command(BaseCommand):
    help = 'Add sample welcome videos for new users'

    def handle(self, *args, **options):
        # Sample videos (replace with your actual video URLs)
        sample_videos = [
            {
                'title': 'Welcome Video 1',
                'video_url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
                'order': 1,
                'is_active': True
            },
            {
                'title': 'Welcome Video 2', 
                'video_url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_2mb.mp4',
                'order': 2,
                'is_active': True
            },
            {
                'title': 'Welcome Video 3',
                'video_url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_5mb.mp4',
                'order': 3,
                'is_active': True
            }
        ]
        
        created_count = 0
        for video_data in sample_videos:
            video, created = WelcomeVideo.objects.get_or_create(
                title=video_data['title'],
                defaults=video_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created video: {video.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Video already exists: {video.title}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {len(sample_videos)} videos. Created {created_count} new videos.')
        )
