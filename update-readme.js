const axios = require('axios');
const Parser = require('rss-parser');
const fs = require('fs').promises;
const path = require('path');

class GitHubProfileUpdater {
    constructor() {
        this.username = process.env.GITHUB_ACTOR || process.env.GITHUB_USERNAME || 'your-username';
        this.token = process.env.GITHUB_TOKEN;
        this.baseURL = 'https://api.github.com';
        
        if (!this.token) {
            console.error('GITHUB_TOKEN environment variable is required');
            process.exit(1);
        }
        
        this.headers = {
            'Authorization': `token ${this.token}`,
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': `${this.username}-readme-updater`
        };
        
        this.config = {
            bio: process.env.BIO || 'Full Stack Developer & Open Source Enthusiast',
            currentProject: process.env.CURRENT_PROJECT || 'Building Amazing Applications',
            learning: process.env.LEARNING || 'Cloud Computing & AI/ML',
            collaboration: process.env.COLLABORATION || 'Open Source Projects',
            askMeAbout: process.env.ASK_ME_ABOUT || 'Python, JavaScript, Cloud Architecture',
            funFact: process.env.FUN_FACT || 'I debug with console.log and I\'m not ashamed!',
            blogRSSUrl: process.env.BLOG_RSS_URL || '',
            socialTwitter: process.env.SOCIAL_TWITTER || '',
            socialLinkedIn: process.env.SOCIAL_LINKEDIN || '',
            socialYouTube: process.env.SOCIAL_YOUTUBE || '',
            socialInstagram: process.env.SOCIAL_INSTAGRAM || '',
            socialDiscord: process.env.SOCIAL_DISCORD || '',
            socialWebsite: process.env.SOCIAL_WEBSITE || ''
        };
        
        this.parser = new Parser();
    }
    
    async makeGitHubRequest(endpoint) {
        try {
            const response = await axios.get(`${this.baseURL}${endpoint}`, {
                headers: this.headers,
                timeout: 10000
            });
            return response.data;
        } catch (error) {
            if (error.response?.status === 403) {
                console.warn(`Rate limited or forbidden: ${endpoint}`);
            } else {
                console.warn(`Request failed: ${endpoint}`, error.message);
            }
            return {};
        }
    }
    
    async getUserInfo() {
        console.log('Fetching user information...');
        return await this.makeGitHubRequest(`/users/${this.username}`);
    }
    
    async getRepositories(count = 100) {
        console.log('Fetching repositories...');
        
        const reposByStars = await this.makeGitHubRequest(`/users/${this.username}/repos?sort=stars&per_page=${count}`);
        const reposByUpdated = await this.makeGitHubRequest(`/users/${this.username}/repos?sort=updated&per_page=${count}`);
        
        // Combine and deduplicate, filter out forks
        const allRepos = {};
        [...(reposByStars || []), ...(reposByUpdated || [])].forEach(repo => {
            if (!repo.fork) {
                allRepos[repo.id] = repo;
            }
        });
        
        return Object.values(allRepos);
    }
    
    async getBlogPosts(count = 5) {
        if (!this.config.blogRSSUrl) {
            return '';
        }
        
        console.log('Fetching blog posts...');
        try {
            const feed = await this.parser.parseURL(this.config.blogRSSUrl);
            const posts = feed.items.slice(0, count).map(item => {
                const date = item.pubDate ? ` - ${new Date(item.pubDate).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}` : '';
                return `- [${item.title}](${item.link})${date}`;
            });
            
            return posts.join('\\n');
        } catch (error) {
            console.warn('Failed to fetch blog posts:', error.message);
            return '';
        }
    }
    
    generateTechBadges(technologies) {
        const techConfigs = {
            'Python': { color: '3776AB', logo: 'python' },
            'JavaScript': { color: 'F7DF1E', logo: 'javascript', logoColor: 'black' },
            'TypeScript': { color: '3178C6', logo: 'typescript' },
            'Java': { color: 'ED8B00', logo: 'java' },
            'C++': { color: '00599C', logo: 'c%2B%2B' },
            'React': { color: '61DAFB', logo: 'react', logoColor: 'black' },
            'Node.js': { color: '339933', logo: 'node.js' },
            'Vue.js': { color: '4FC08D', logo: 'vue.js' },
            'Angular': { color: 'DD0031', logo: 'angular' },
            'Django': { color: '092E20', logo: 'django' },
            'Flask': { color: '000000', logo: 'flask' },
            'Express.js': { color: '000000', logo: 'express' },
            'MongoDB': { color: '47A248', logo: 'mongodb' },
            'PostgreSQL': { color: '4169E1', logo: 'postgresql' },
            'MySQL': { color: '4479A1', logo: 'mysql' },
            'Redis': { color: 'DC382D', logo: 'redis' },
            'Docker': { color: '2496ED', logo: 'docker' },
            'Kubernetes': { color: '326CE5', logo: 'kubernetes' },
            'AWS': { color: 'FF9900', logo: 'amazon-aws', logoColor: 'black' },
            'Google Cloud': { color: '4285F4', logo: 'google-cloud' },
            'Azure': { color: '0078D4', logo: 'microsoft-azure' },
            'Git': { color: 'F05032', logo: 'git' },
            'Linux': { color: 'FCC624', logo: 'linux', logoColor: 'black' }
        };
        
        const badges = technologies.map(tech => {
            const config = techConfigs[tech] || { color: 'grey', logo: tech.toLowerCase().replace(' ', '-') };
            const logoColor = config.logoColor || 'white';
            const techName = tech.replace(' ', '%20');
            
            return `![${tech}](https://img.shields.io/badge/${techName}-${config.color}?style=for-the-badge&logo=${config.logo}&logoColor=${logoColor})`;
        });
        
        // Split badges into rows for better formatting
        const badgeRows = [];
        for (let i = 0; i < badges.length; i += 4) {
            badgeRows.push(badges.slice(i, i + 4).join(' '));
        }
        
        return badgeRows.join('\\n');
    }
    
    generateSocialLinks() {
        const links = [];
        const socialConfigs = {
            socialTwitter: { color: '1DA1F2', logo: 'twitter', label: 'Twitter' },
            socialLinkedIn: { color: '0077B5', logo: 'linkedin', label: 'LinkedIn' },
            socialYouTube: { color: 'FF0000', logo: 'youtube', label: 'YouTube' },
            socialInstagram: { color: 'E4405F', logo: 'instagram', label: 'Instagram' },
            socialDiscord: { color: '7289DA', logo: 'discord', label: 'Discord' },
            socialWebsite: { color: '000000', logo: 'google-chrome', label: 'Website' }
        };
        
        Object.entries(socialConfigs).forEach(([key, config]) => {
            const url = this.config[key];
            if (url) {
                const badge = `[![${config.label}](https://img.shields.io/badge/${config.label}-${config.color}?style=for-the-badge&logo=${config.logo}&logoColor=white)](${url})`;
                links.push(badge);
            }
        });
        
        return links.join('\\n');
    }
    
    generateFeaturedRepos(repos, count = 6) {
        if (!repos || repos.length === 0) {
            return '';
        }
        
        // Sort repos by stars + forks for featured selection
        const featured = repos
            .sort((a, b) => (b.stargazers_count + b.forks_count) - (a.stargazers_count + a.forks_count))
            .slice(0, count);
        
        const cards = featured.map(repo => {
            return `<a href="${repo.html_url}">
  <img src="https://github-readme-stats.vercel.app/api/pin/?username=${this.username}&repo=${repo.name}&theme=radical" />
</a>`;
        });
        
        return cards.join('\\n');
    }
    
    async updateReadme() {
        console.log('Starting README update process...');
        
        const templatePath = 'README.template.md';
        
        try {
            // Check if template exists
            await fs.access(templatePath);
        } catch (error) {
            console.error(`Template file ${templatePath} not found!`);
            return false;
        }
        
        try {
            // Read template
            const template = await fs.readFile(templatePath, 'utf8');
            
            // Get data
            const [userInfo, repos] = await Promise.all([
                this.getUserInfo(),
                this.getRepositories()
            ]);
            
            const blogPosts = await this.getBlogPosts();
            
            // Determine technologies from repositories
            const repoLanguages = repos
                .map(repo => repo.language)
                .filter(lang => lang);
            
            const languageCounts = {};
            repoLanguages.forEach(lang => {
                languageCounts[lang] = (languageCounts[lang] || 0) + 1;
            });
            
            const topLanguages = Object.keys(languageCounts)
                .sort((a, b) => languageCounts[b] - languageCounts[a])
                .slice(0, 8);
            
            // Build replacement dictionary
            const replacements = {
                USERNAME: this.username,
                BIO: this.config.bio,
                CURRENT_PROJECT: this.config.currentProject,
                LEARNING: this.config.learning,
                COLLABORATION: this.config.collaboration,
                ASK_ME_ABOUT: this.config.askMeAbout,
                EMAIL: userInfo.email || 'your.email@example.com',
                FUN_FACT: this.config.funFact,
                TECH_BADGES: this.generateTechBadges(topLanguages),
                BLOG_POSTS: blogPosts,
                FEATURED_REPOSITORIES: this.generateFeaturedRepos(repos),
                SOCIAL_LINKS: this.generateSocialLinks(),
                LAST_UPDATED: new Date().toISOString().replace('T', ' ').substr(0, 19) + ' UTC'
            };
            
            // Replace placeholders
            let updatedContent = template;
            Object.entries(replacements).forEach(([key, value]) => {
                const placeholder = `{{${key}}}`;
                updatedContent = updatedContent.replace(new RegExp(placeholder, 'g'), value);
            });
            
            // Write updated README
            await fs.writeFile('README.md', updatedContent, 'utf8');
            
            console.log('README.md updated successfully!');
            
            // Print stats
            const totalStars = repos.reduce((sum, repo) => sum + (repo.stargazers_count || 0), 0);
            const totalForks = repos.reduce((sum, repo) => sum + (repo.forks_count || 0), 0);
            console.log(`Statistics: ${repos.length} repos, ${totalStars} stars, ${totalForks} forks`);
            
            return true;
            
        } catch (error) {
            console.error('Failed to update README:', error.message);
            return false;
        }
    }
}

// Main execution
async function main() {
    console.log('Dynamic GitHub Profile README Updater (Node.js)');
    console.log('================================================');
    
    const updater = new GitHubProfileUpdater();
    const success = await updater.updateReadme();
    
    if (success) {
        console.log('README update completed successfully!');
        process.exit(0);
    } else {
        console.error('README update failed!');
        process.exit(1);
    }
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = GitHubProfileUpdater;