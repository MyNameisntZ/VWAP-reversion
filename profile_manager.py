"""
Profile Manager for Hybrid-Safe Trading Bot
Handles saving and loading user profiles with tickers and settings
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class ProfileManager:
    """Manages user profiles for the trading bot."""
    
    def __init__(self, profiles_dir: str = "profiles"):
        """
        Initialize the profile manager.
        
        Args:
            profiles_dir (str): Directory to store profile files
        """
        self.profiles_dir = profiles_dir
        self.current_profile = "default"
        self.profile_data = {}
        
        # Create profiles directory if it doesn't exist
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir)
        
        # Load default profile
        self.load_profile("default")
    
    def get_profile_path(self, profile_name: str) -> str:
        """Get the file path for a profile."""
        return os.path.join(self.profiles_dir, f"{profile_name}.json")
    
    def save_profile(self, profile_name: str, data: Dict[str, Any]) -> bool:
        """
        Save profile data to file.
        
        Args:
            profile_name (str): Name of the profile
            data (Dict): Profile data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            profile_path = self.get_profile_path(profile_name)
            
            # Add metadata
            profile_data = {
                "name": profile_name,
                "created": data.get("created", datetime.now().isoformat()),
                "last_modified": datetime.now().isoformat(),
                "version": "1.0",
                "data": data
            }
            
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving profile {profile_name}: {e}")
            return False
    
    def load_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """
        Load profile data from file.
        
        Args:
            profile_name (str): Name of the profile to load
            
        Returns:
            Dict: Profile data if successful, None otherwise
        """
        try:
            profile_path = self.get_profile_path(profile_name)
            
            if not os.path.exists(profile_path):
                # Return None if profile doesn't exist (don't auto-create)
                return None
            
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            # Return the data section
            return profile_data.get("data", {})
            
        except Exception as e:
            print(f"Error loading profile {profile_name}: {e}")
            return None
    
    def get_default_profile_data(self) -> Dict[str, Any]:
        """Get default profile data."""
        return {
            "symbols": ["AAPL", "NVDA", "TSLA", "AMZN", "META"],
            "trading_settings": {
                "position_size": 100.0,
                "stop_loss_pct": 3.0,
                "take_profit_pct": 8.0
            },
            "data_settings": {
                "refresh_interval": 60,
                "auto_refresh": False
            },
            "created": datetime.now().isoformat()
        }
    
    def list_profiles(self) -> List[str]:
        """Get list of available profiles."""
        profiles = []
        try:
            for filename in os.listdir(self.profiles_dir):
                if filename.endswith('.json'):
                    profile_name = filename[:-5]  # Remove .json extension
                    profiles.append(profile_name)
        except Exception as e:
            print(f"Error listing profiles: {e}")
        
        return sorted(profiles)
    
    def delete_profile(self, profile_name: str) -> bool:
        """
        Delete a profile.
        
        Args:
            profile_name (str): Name of the profile to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            profile_path = self.get_profile_path(profile_name)
            if os.path.exists(profile_path):
                os.remove(profile_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting profile {profile_name}: {e}")
            return False
    
    def export_profile(self, profile_name: str, export_path: str) -> bool:
        """
        Export profile to a specific path.
        
        Args:
            profile_name (str): Name of the profile to export
            export_path (str): Path to export the profile to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            profile_path = self.get_profile_path(profile_name)
            if os.path.exists(profile_path):
                import shutil
                shutil.copy2(profile_path, export_path)
                return True
            return False
        except Exception as e:
            print(f"Error exporting profile {profile_name}: {e}")
            return False
    
    def import_profile(self, import_path: str, profile_name: str = None) -> bool:
        """
        Import profile from a file.
        
        Args:
            import_path (str): Path to the profile file to import
            profile_name (str): Name for the imported profile (if None, uses filename)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(import_path):
                return False
            
            if profile_name is None:
                profile_name = os.path.splitext(os.path.basename(import_path))[0]
            
            profile_path = self.get_profile_path(profile_name)
            import shutil
            shutil.copy2(import_path, profile_path)
            return True
            
        except Exception as e:
            print(f"Error importing profile: {e}")
            return False
    
    def get_current_profile_data(self) -> Dict[str, Any]:
        """Get data from the currently loaded profile."""
        return self.profile_data
    
    def update_current_profile(self, data: Dict[str, Any]) -> None:
        """Update the current profile data."""
        self.profile_data.update(data)
    
    def save_current_profile(self) -> bool:
        """Save the current profile data."""
        return self.save_profile(self.current_profile, self.profile_data)
    
    def switch_profile(self, profile_name: str) -> bool:
        """
        Switch to a different profile.
        
        Args:
            profile_name (str): Name of the profile to switch to
            
        Returns:
            bool: True if successful, False otherwise
        """
        data = self.load_profile(profile_name)
        if data is not None:
            self.current_profile = profile_name
            self.profile_data = data
            return True
        return False
