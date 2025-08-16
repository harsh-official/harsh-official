#!/usr/bin/env python3
"""
Dynamic GitHub Profile README Updater
Automatically updates GitHub profile README with dynamic content
"""

import os
import sys
import json
import requests
import feedparser
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitHubProfileUpdater:
    def __init__(self):
        """Initialize the GitHub Profile Updater"""
        self.username = os.getenv('GITHUB_ACTOR', os.getenv('GITHUB_USERNAME', 'your-username'))
        self.token = os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        
        if not self.token:
            logger.error("GITHUB_TOKEN environment variable is required")
            sys.exit(1)
            
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': f'{self.username}-readme-updater'
        }
        
        # Configuration from environment variables or defaults
        self.config = {
            'bio': os.getenv('BIO', 'Full Stack Developer & Open Source Enthusiast'),
            'current_project': os.getenv('CURRENT_PROJECT', 'Building Amazing Applications'),
            'learning': os.getenv('LEARNING', 'Cloud Computing & AI/ML'),
            'collaboration': os.getenv('COLLABORATION', 'Open Source Projects'),
            'ask_me_about': os.getenv('ASK_ME_ABOUT', 'Python, JavaScript, Cloud Architecture'),
            'fun_fact': os.getenv('FUN_FACT', 'I debug with print statements and I\'m not ashamed!'),
            'blog_rss_url': os.getenv('BLOG_RSS_URL', ''),
            'social_twitter': os.getenv('SOCIAL_TWITTER', ''),
            'social_linkedin': os.getenv('SOCIAL_LINKEDIN', ''),
            'social_youtube': os.getenv('SOCIAL_YOUTUBE', ''),
            'social_instagram': os.getenv('SOCIAL_INSTAGRAM', ''),
            'social_discord': os.getenv('SOCIAL_DISCORD', ''),
            'social_website': os.getenv('SOCIAL_WEBSITE', ''),
        }

    def make_github_request(self, endpoint):
        """Make a request to GitHub API with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                logger.warning(f"Rate limited or forbidden: {endpoint}")
                return {}
            else:
                logger.warning(f"Request failed {response.status_code}: {endpoint}")
                return {}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {endpoint}: {str(e)}")
            return {}

    def get_user_info(self):
        """Fetch user information from GitHub API"""
        logger.info("Fetching user information...")
        return self.make_github_request(f"/users/{self.username}")

    def get_repositories(self, count=100):
        """Fetch repositories sorted by various metrics"""
        logger.info("Fetching repositories...")
        
        # Get repositories sorted by stars
        repos_by_stars = self.make_github_request(f"/users/{self.username}/repos?sort=stars&per_page={count}")
        
        # Get repositories sorted by updated
        repos_by_updated = self.make_github_request(f"/users/{self.username}/repos?sort=updated&per_page={count}")
        
        # Combine and deduplicate
        all_repos = {}
        for repo in repos_by_stars + repos_by_updated:
            if repo.get('fork', False):  # Skip forks
                continue
            all_repos[repo['id']] = repo
            
        return list(all_repos.values())

    def get_user_stats(self):
        """Calculate user statistics"""
        logger.info("Calculating user statistics...")
        repos = self.get_repositories()
        
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        total_forks = sum(repo.get('forks_count', 0) for repo in repos)
        
        languages = {}
        for repo in repos:
            if repo.get('language'):
                languages[repo['language']] = languages.get(repo['language'], 0) + 1
                
        return {
            'total_repos': len(repos),
            'total_stars': total_stars,
            'total_forks': total_forks,
            'languages': languages
        }

    def get_blog_posts(self, count=5):
        """Fetch latest blog posts from RSS feed"""
        if not self.config['blog_rss_url']:
            return ""
            
        logger.info("Fetching blog posts...")
        try:
            feed = feedparser.parse(self.config['blog_rss_url'])
            posts = []
            
            for entry in feed.entries[:count]:
                title = entry.title
                link = entry.link
                
                # Get publish date if available
                date_str = ""
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    date_obj = datetime(*entry.published_parsed[:6])
                    date_str = f" - {date_obj.strftime('%B %d, %Y')}"
                
                posts.append(f"- [{title}]({link}){date_str}")
                
            return "\n".join(posts)
            
        except Exception as e:
            logger.warning(f"Failed to fetch blog posts: {str(e)}")
            return ""

    def generate_tech_badges(self, technologies):
        """Generate technology badges"""
        tech_configs = {
            'Python': {'color': '3776AB', 'logo': 'python'},
            'JavaScript': {'color': 'F7DF1E', 'logo': 'javascript', 'logoColor': 'black'},
            'TypeScript': {'color': '3178C6', 'logo': 'typescript'},
            'Java': {'color': 'ED8B00', 'logo': 'java'},
            'C++': {'color': '00599C', 'logo': 'c%2B%2B'},
            'React': {'color': '61DAFB', 'logo': 'react', 'logoColor': 'black'},
            'Node.js': {'color': '339933', 'logo': 'node.js'},
            'Vue.js': {'color': '4FC08D', 'logo': 'vue.js'},
            'Angular': {'color': 'DD0031', 'logo': 'angular'},
            'Django': {'color': '092E20', 'logo': 'django'},
            'Flask': {'color': '000000', 'logo': 'flask'},
            'Express.js': {'color': '000000', 'logo': 'express'},
            'MongoDB': {'color': '47A248', 'logo': 'mongodb'},
            'PostgreSQL': {'color': '4169E1', 'logo': 'postgresql'},
            'MySQL': {'color': '4479A1', 'logo': 'mysql'},
            'Redis': {'color': 'DC382D', 'logo': 'redis'},
            'Docker': {'color': '2496ED', 'logo': 'docker'},
            'Kubernetes': {'color': '326CE5', 'logo': 'kubernetes'},
            'AWS': {'color': 'FF9900', 'logo': 'amazon-aws', 'logoColor': 'black'},
            'Google Cloud': {'color': '4285F4', 'logo': 'google-cloud'},
            'Azure': {'color': '0078D4', 'logo': 'microsoft-azure'},
            'Git': {'color': 'F05032', 'logo': 'git'},
            'Linux': {'color': 'FCC624', 'logo': 'linux', 'logoColor': 'black'},
            'TensorFlow': {'color': 'FF6F00', 'logo': 'tensorflow'},
            'PyTorch': {'color': 'EE4C2C', 'logo': 'pytorch'},
        }
        
        badges = []
        for tech in technologies:
            config = tech_configs.get(tech, {'color': 'grey', 'logo': tech.lower().replace(' ', '-')})
            logo_color = config.get('logoColor', 'white')
            
            badge = f"![{tech}](https://img.shields.io/badge/{tech.replace(' ', '%20')}-{config['color']}?style=for-the-badge&logo={config['logo']}&logoColor={logo_color})"
            badges.append(badge)
        
        # Split badges into rows for better formatting
        badge_rows = []
        for i in range(0, len(badges), 4):  # 4 badges per row
            badge_rows.append(' '.join(badges[i:i+4]))
        
        return '\n'.join(badge_rows)

    def generate_social_links(self):
        """Generate social media links with badges"""
        links = []
        
        social_configs = {
            'twitter': {'color': '1DA1F2', 'logo': 'twitter', 'label': 'Twitter'},
            'linkedin': {'color': '0077B5', 'logo': 'linkedin', 'label': 'LinkedIn'},
            'youtube': {'color': 'FF0000', 'logo': 'youtube', 'label': 'YouTube'},
            'instagram': {'color': 'E4405F', 'logo': 'instagram', 'label': 'Instagram'},
            'discord': {'color': '7289DA', 'logo': 'discord', 'label': 'Discord'},
            'website': {'color': '000000', 'logo': 'google-chrome', 'label': 'Website'},
        }
        
        for platform, config in social_configs.items():
            url = self.config.get(f'social_{platform}')
            if url:
                badge = f"[![{config['label']}](https://img.shields.io/badge/{config['label']}-{config['color']}?style=for-the-badge&logo={config['logo']}&logoColor=white)]({url})"
                links.append(badge)
        
        return '\n'.join(links)

    def generate_featured_repos(self, repos, count=6):
        """Generate featured repository cards"""
        if not repos:
            return ""
            
        # Sort repos by stars + forks for featured selection
        featured = sorted(repos, key=lambda x: x.get('stargazers_count', 0) + x.get('forks_count', 0), reverse=True)[:count]
        
        cards = []
        for repo in featured:
            card = f"""<a href="{repo['html_url']}">
  <img src="https://github-readme-stats.vercel.app/api/pin/?username={self.username}&repo={repo['name']}&theme=radical" />
</a>"""
            cards.append(card)
        
        return '\n'.join(cards)

    def update_readme(self):
        """Main function to update README"""
        logger.info("Starting README update process...")
        
        # Check if template exists
        template_path = 'README.template.md'
        if not os.path.exists(template_path):
            logger.error(f"Template file {template_path} not found!")
            return False
        
        # Read template
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except Exception as e:
            logger.error(f"Failed to read template: {str(e)}")
            return False
        
        # Get data
        user_info = self.get_user_info()
        repos = self.get_repositories()
        user_stats = self.get_user_stats()
        
        # Determine technologies from repositories
        repo_languages = [repo.get('language') for repo in repos if repo.get('language')]
        top_languages = sorted(set(repo_languages), key=repo_languages.count, reverse=True)[:8]
        
        # Build replacement dictionary
        replacements = {
            'USERNAME': self.username,
            'BIO': self.config['bio'],
            'CURRENT_PROJECT': self.config['current_project'],
            'LEARNING': self.config['learning'],
            'COLLABORATION': self.config['collaboration'],
            'ASK_ME_ABOUT': self.config['ask_me_about'],
            'EMAIL': user_info.get('email', 'your.email@example.com'),
            'FUN_FACT': self.config['fun_fact'],
            'TECH_BADGES': self.generate_tech_badges(top_languages),
            'BLOG_POSTS': self.get_blog_posts(),
            'FEATURED_REPOSITORIES': self.generate_featured_repos(repos),
            'SOCIAL_LINKS': self.generate_social_links(),
            'LAST_UPDATED': datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        }
        
        # Replace placeholders
        updated_content = template
        for key, value in replacements.items():
            placeholder = '{{' + key + '}}'
            updated_content = updated_content.replace(placeholder, str(value))
        
        # Write updated README
        try:
            with open('README.md', 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.info("README.md updated successfully!")
            
            # Print stats
            logger.info(f"Statistics: {user_stats['total_repos']} repos, "
                       f"{user_stats['total_stars']} stars, "
                       f"{user_stats['total_forks']} forks")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to write README: {str(e)}")
            return False

def main():
    """Main entry point"""
    logger.info("Dynamic GitHub Profile README Updater")
    logger.info("====================================")
    
    updater = GitHubProfileUpdater()
    success = updater.update_readme()
    
    if success:
        logger.info("README update completed successfully!")
        sys.exit(0)
    else:
        logger.error("README update failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()