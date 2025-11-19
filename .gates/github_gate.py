#!/usr/bin/env python3
"""
GitHub Gate — максимальная интеграция с GitHub

Требует: GITHUB_TOKEN (Personal Access Token with all scopes)
"""

import os
import requests
from datetime import datetime, timezone


class GitHubGate:
    """Универсальный интерфейс к GitHub"""
    
    BASE_URL = 'https://api.github.com'
    
    def __init__(self, token=None):
        self.token = token or os.environ.get('GITHUB_TOKEN')
        
        if not self.token:
            raise ValueError(
                "❌ GITHUB_TOKEN не найден.\n"
                "Получите: https://github.com/settings/tokens/new\n"
                "Scopes: ВСЕ (максимум прав)"
            )
        
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    # === READ ===
    
    def get_repos(self, username=None):
        """Получить все репозитории"""
        if username:
            url = f'{self.BASE_URL}/users/{username}/repos'
        else:
            url = f'{self.BASE_URL}/user/repos'
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_commits(self, repo, owner=None, since=None):
        """Получить коммиты"""
        if not owner:
            owner = self.get_user()['login']
        
        url = f'{self.BASE_URL}/repos/{owner}/{repo}/commits'
        params = {'since': since} if since else {}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_user(self):
        """Получить информацию о пользователе"""
        response = requests.get(f'{self.BASE_URL}/user', headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    # === WRITE ===
    
    def create_repo(self, name, description=None, private=False):
        """Создать репозиторий"""
        url = f'{self.BASE_URL}/user/repos'
        
        data = {
            'name': name,
            'description': description,
            'private': private,
            'auto_init': True
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def create_webhook(self, repo, owner, callback_url, events=['push']):
        """Создать webhook"""
        url = f'{self.BASE_URL}/repos/{owner}/{repo}/hooks'
        
        data = {
            'name': 'web',
            'active': True,
            'events': events,
            'config': {
                'url': callback_url,
                'content_type': 'json'
            }
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    # === EXPORT ===
    
    def export_substance(self):
        """Экспорт всех данных GitHub"""
        user = self.get_user()
        repos = self.get_repos()
        
        substance = {
            'provider': 'github',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'user': user,
                'repos': repos,
                'repos_count': len(repos)
            }
        }
        
        # Последние коммиты из всех репозиториев
        recent_commits = []
        for repo in repos[:10]:  # Топ-10 репозиториев
            try:
                commits = self.get_commits(repo['name'], since='2025-11-01T00:00:00Z')
                recent_commits.extend(commits[:5])
            except:
                pass
        
        substance['data']['recent_commits'] = recent_commits
        substance['data']['commits_count'] = len(recent_commits)
        
        return substance


if __name__ == '__main__':
    try:
        gate = GitHubGate()
        
        print("🔐 GitHub Gate\n")
        
        user = gate.get_user()
        print(f"✅ Пользователь: {user['login']}")
        print(f"   Имя: {user['name']}")
        print(f"   Repos: {user['public_repos']}\n")
        
        repos = gate.get_repos()
        print(f"📦 Репозитории ({len(repos)}):\n")
        
        for repo in repos[:10]:
            print(f"   • {repo['name']}")
        
        print(f"\n📊 Экспорт Substance...")
        substance = gate.export_substance()
        print(f"✅ Экспортировано:")
        print(f"   Repos: {substance['data']['repos_count']}")
        print(f"   Recent commits: {substance['data']['commits_count']}")
        
    except ValueError as e:
        print(str(e))
    except Exception as e:
        print(f"❌ Ошибка: {e}")
