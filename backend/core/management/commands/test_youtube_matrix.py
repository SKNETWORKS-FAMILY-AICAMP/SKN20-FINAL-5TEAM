from django.core.management.base import BaseCommand
from django.test import RequestFactory
from core.views.youtube_recommendation import get_youtube_recommendations
from core.utils.curated_videos import QUEST_VIDEO_MAP
import json

class Command(BaseCommand):
    help = 'Verify that all 30 Quest-Dimension combinations return the correct curated video'

    def handle(self, *args, **kwargs):
        factory = RequestFactory()
        
        total_tests = 0
        passed_tests = 0
        
        self.stdout.write(self.style.WARNING('Starting Video Matrix Verification...'))

        for quest, dimensions in QUEST_VIDEO_MAP.items():
            for dim, expected_video in dimensions.items():
                total_tests += 1
                
                # Construct request data
                # We simulate a "weakest dimension" by giving it a very low score
                data = {
                    'quest_title': quest,
                    'dimensions': {
                        # Set the target dimension to score 0 (weakest)
                        dim: {'score': 0, 'percentage': 0},
                        # Set others to high score
                        'other': {'score': 100, 'percentage': 100}
                    }
                }
                
                request = factory.post(
                    '/api/v1/youtube/recommendation/',
                    data=data,
                    content_type='application/json'
                )
                
                # Execute view
                response = get_youtube_recommendations(request)
                
                if response.status_code == 200:
                    response_data = response.data
                    videos = response_data.get('videos', [])
                    
                    if videos and videos[0]['url'] == expected_video['url']:
                        passed_tests += 1
                        self.stdout.write(self.style.SUCCESS(f'[PASS] {quest} - {dim}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'[FAIL] {quest} - {dim}'))
                        self.stdout.write(f"  Expected: {expected_video['url']}")
                        self.stdout.write(f"  Got: {videos[0]['url'] if videos else 'None'}")
                else:
                    self.stdout.write(self.style.ERROR(f'[ERROR] {quest} - {dim} (Status {response.status_code})'))

        self.stdout.write('--------------------------------------------------')
        if passed_tests == total_tests:
            self.stdout.write(self.style.SUCCESS(f'ALL TESTS PASSED ({passed_tests}/{total_tests})'))
        else:
            self.stdout.write(self.style.ERROR(f'SOME TESTS FAILED ({passed_tests}/{total_tests})'))
