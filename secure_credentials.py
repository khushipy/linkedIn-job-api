#!/usr/bin/env python3
"""
Secure Credential Management for LinkedIn Automation
Provides multiple secure ways to handle LinkedIn credentials
"""

import os
import getpass
import keyring
import base64
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import json

class SecureCredentialManager:
    """Secure credential management with multiple storage options"""
    
    def __init__(self):
        self.service_name = "LinkedIn_Automation"
        load_dotenv()
    
    def generate_key(self):
        """Generate encryption key for local storage"""
        return Fernet.generate_key()
    
    def encrypt_password(self, password: str, key: bytes) -> str:
        """Encrypt password using Fernet encryption"""
        f = Fernet(key)
        encrypted_password = f.encrypt(password.encode())
        return base64.urlsafe_b64encode(encrypted_password).decode()
    
    def decrypt_password(self, encrypted_password: str, key: bytes) -> str:
        """Decrypt password using Fernet encryption"""
        f = Fernet(key)
        encrypted_data = base64.urlsafe_b64decode(encrypted_password.encode())
        decrypted_password = f.decrypt(encrypted_data)
        return decrypted_password.decode()
    
    def save_to_keyring(self, username: str, password: str):
        """Save credentials to system keyring (most secure)"""
        try:
            keyring.set_password(self.service_name, username, password)
            print("✅ Credentials saved securely to system keyring")
            return True
        except Exception as e:
            print(f" Failed to save to keyring: {str(e)}")
            return False
    
    def get_from_keyring(self, username: str) -> str:
        """Retrieve password from system keyring"""
        try:
            password = keyring.get_password(self.service_name, username)
            return password
        except Exception as e:
            print(f"Failed to retrieve from keyring: {str(e)}")
            return None
    
    def save_to_env_file(self, username: str, password: str):
        """Save credentials to .env file (less secure but convenient)"""
        try:
            env_content = f"""# LinkedIn Automation Credentials
LINKEDIN_EMAIL={username}
LINKEDIN_PASSWORD={password}

# Security Note: This file contains sensitive information
# Make sure it's in .gitignore and not shared
"""
            with open('.env', 'w') as f:
                f.write(env_content)
            print(" Credentials saved to .env file")
            print("  Make sure .env is in your .gitignore file!")
            return True
        except Exception as e:
            print(f" Failed to save to .env file: {str(e)}")
            return False
    
    def get_from_env(self):
        """Get credentials from environment variables"""
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')
        return email, password
    
    def save_encrypted_local(self, username: str, password: str):
        """Save encrypted credentials to local file"""
        try:
            key = self.generate_key()
            encrypted_password = self.encrypt_password(password, key)
            
            # Save key and encrypted data separately
            with open('.linkedin_key', 'wb') as f:
                f.write(key)
            
            credentials = {
                'username': username,
                'encrypted_password': encrypted_password
            }
            
            with open('.linkedin_creds', 'w') as f:
                json.dump(credentials, f)
            
            print(" Credentials encrypted and saved locally")
            print(" Keep .linkedin_key file secure!")
            return True
        except Exception as e:
            print(f"Failed to save encrypted credentials: {str(e)}")
            return False
    
    def get_encrypted_local(self):
        """Get credentials from encrypted local files"""
        try:
            # Read key
            with open('.linkedin_key', 'rb') as f:
                key = f.read()
            
            # Read encrypted credentials
            with open('.linkedin_creds', 'r') as f:
                credentials = json.load(f)
            
            username = credentials['username']
            password = self.decrypt_password(credentials['encrypted_password'], key)
            
            return username, password
        except Exception as e:
            print(f" Failed to retrieve encrypted credentials: {str(e)}")
            return None, None
    
    def prompt_secure_input(self):
        """Securely prompt for credentials without storing"""
        print("\n SECURE CREDENTIAL INPUT")
        print("Your credentials will only be stored in memory during execution")
        print("They will NOT be saved to any files")
        
        email = input("LinkedIn Email: ")
        password = getpass.getpass("LinkedIn Password (hidden): ")
        
        return email, password
    
    def get_credentials_interactive(self):
        """Interactive credential selection with multiple options"""
        print("\n SECURE CREDENTIAL MANAGEMENT")
        print("Choose how you want to provide your LinkedIn credentials:")
        print()
        print("1.  System Keyring (Most Secure - saves to Windows Credential Manager)")
        print("2.  Environment File (.env file - convenient but less secure)")
        print("3.  Encrypted Local Storage (encrypted files)")
        print("4.  Manual Input Each Time (most secure, no storage)")
        print("5.  Use Existing Saved Credentials")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-5): ").strip()
                
                if choice == "1":
                    return self.setup_keyring_credentials()
                elif choice == "2":
                    return self.setup_env_credentials()
                elif choice == "3":
                    return self.setup_encrypted_credentials()
                elif choice == "4":
                    return self.prompt_secure_input()
                elif choice == "5":
                    return self.load_existing_credentials()
                else:
                    print(" Invalid choice. Please enter 1-5.")
            except KeyboardInterrupt:
                print("\n Operation cancelled")
                return None, None
    
    def setup_keyring_credentials(self):
        """Setup credentials using system keyring"""
        email, password = self.prompt_secure_input()
        if email and password:
            if self.save_to_keyring(email, password):
                return email, password
        return None, None
    
    def setup_env_credentials(self):
        """Setup credentials using .env file"""
        email, password = self.prompt_secure_input()
        if email and password:
            if self.save_to_env_file(email, password):
                return email, password
        return None, None
    
    def setup_encrypted_credentials(self):
        """Setup encrypted local credentials"""
        email, password = self.prompt_secure_input()
        if email and password:
            if self.save_encrypted_local(email, password):
                return email, password
        return None, None
    
    def load_existing_credentials(self):
        """Try to load from existing storage methods"""
        print("\n🔍 Checking for existing credentials...")
        
        # Try keyring first
        email_env, _ = self.get_from_env()
        if email_env:
            password = self.get_from_keyring(email_env)
            if password:
                print(" Found credentials in system keyring")
                return email_env, password
        
        # Try .env file
        email, password = self.get_from_env()
        if email and password:
            print(" Found credentials in .env file")
            return email, password
        
        # Try encrypted local
        email, password = self.get_encrypted_local()
        if email and password:
            print(" Found encrypted local credentials")
            return email, password
        
        print(" No existing credentials found")
        return None, None
    
    def clear_all_credentials(self):
        """Clear all stored credentials"""
        print("\n CLEARING ALL STORED CREDENTIALS")
        
        # Clear keyring
        try:
            email_env, _ = self.get_from_env()
            if email_env:
                keyring.delete_password(self.service_name, email_env)
                print("Cleared keyring credentials")
        except:
            pass
        
        # Clear .env file
        try:
            if os.path.exists('.env'):
                os.remove('.env')
                print(" Cleared .env file")
        except:
            pass
        
        # Clear encrypted files
        try:
            if os.path.exists('.linkedin_key'):
                os.remove('.linkedin_key')
            if os.path.exists('.linkedin_creds'):
                os.remove('.linkedin_creds')
                print(" Cleared encrypted local files")
        except:
            pass
        
        print(" All credentials cleared")

def main():
    """Test the secure credential manager"""
    manager = SecureCredentialManager()
    
    print("LinkedIn Automation - Secure Credential Manager")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Setup/Get Credentials")
        print("2. Clear All Credentials")
        print("3. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            email, password = manager.get_credentials_interactive()
            if email and password:
                print(f"\n Credentials ready for: {email}")
                print(" Password is securely loaded")
            else:
                print(" Failed to get credentials")
        
        elif choice == "2":
            manager.clear_all_credentials()
        
        elif choice == "3":
            break
        
        else:
            print(" Invalid choice")

if __name__ == "__main__":
    main()
