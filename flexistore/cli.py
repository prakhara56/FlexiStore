import argparse
import os
from dotenv import load_dotenv
from azure.core.exceptions import AzureError
from botocore.exceptions import BotoCoreError, ClientError
from .azure import AzureStorageManager
from .aws import AWSStorageManager

load_dotenv()

def parse_args():
    parser = argparse.ArgumentParser(description="FlexiStore interactive CLI")

    parser.add_argument(
        "--provider",
        choices=["azure", "aws"],
        help="Storage provider to use (default: value of FLEXISTORE_PROVIDER or azure)",
    )

    ssl_group = parser.add_mutually_exclusive_group()
    ssl_group.add_argument(
        "--no-verify-ssl",
        action="store_false",
        dest="verify_ssl",
        help="Disable SSL certificate verification for AWS (default: enabled)",
    )
    ssl_group.add_argument(
        "--verify-ssl",
        action="store_true",
        dest="verify_ssl",
        help="Enable SSL certificate verification for AWS (default)",
    )
    parser.set_defaults(verify_ssl=False)
    
    return parser.parse_args()

def print_menu():
    print("\n=== FlexiStore CLI ===")
    print("1) Upload a file")
    print("2) List blobs")
    print("3) Download a blob")
    print("4) Delete a blob")
    print("0) Exit")

def confirm(prompt: str) -> bool:
    ans = input(f"{prompt} (y/n): ").strip().lower()
    return ans == 'y'

def get_env_or_prompt(env_var: str, prompt_text: str) -> str:
    val = os.getenv(env_var, "").strip()
    if not val:
        val = input(f"{prompt_text}: ").strip()
    return val

def main():
    args = parse_args()
    provider = args.provider or os.getenv("FLEXISTORE_PROVIDER", "azure").lower()

    if provider == "aws":
        bucket = get_env_or_prompt("AWS_BUCKET", "S3 bucket name")
        region = get_env_or_prompt("AWS_REGION", "AWS region")
        access_key = get_env_or_prompt("AWS_ACCESS_KEY_ID", "AWS access key ID")
        secret_key = get_env_or_prompt("AWS_SECRET_ACCESS_KEY", "AWS secret access key")
        try:
            mgr = AWSStorageManager(
                bucket=bucket,
                region=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                verify_ssl=args.verify_ssl,
            )
        except (BotoCoreError, ClientError) as e:
            print(f"[Fatal] Unable to initialize AWSStorageManager: {e}")
            return
    elif provider == "azure":
        conn_str = get_env_or_prompt("AZURE_CONN_STRING", "Azure connection string")
        container = get_env_or_prompt("AZURE_CONTAINER", "Container name")

        try:
            mgr = AzureStorageManager(conn_str=conn_str, container=container)
        except AzureError as e:
            print(f"[Fatal] Unable to initialize AzureStorageManager: {e}")
            return
        
    else:
        print(f"[Fatal] Unknown provider '{provider}'. Please specify either 'azure' or 'aws'.")
        return

    while True:
        print_menu()
        choice = input("Select an option: ").strip()
        
        if choice == '0':
            print("Goodbye!")
            break

        elif choice == '1':
            local = input("  Local file path to upload: ").strip()
            remote = input("  Remote blob path: ").strip()
            if confirm(f"Upload '{local}' → '{remote}'?"):
                try:
                    mgr.upload_file(local, remote)
                except Exception as e:
                    print(f"  ❌ Upload error: {e}")
                else:
                    print("  ✅ Upload complete.")
            else:
                print("  ❌ Cancelled.")

        elif choice == '2':
            prefix = input("  Remote prefix to list (e.g. 'backups/'): ").strip()
            try:
                blobs = mgr.list_files(prefix)
            except Exception as e:
                print(f"  ❌ List error: {e}")
            else:
                print(f"  Found {len(blobs)} blobs:")
                for b in blobs:
                    print("   -", b)

        elif choice == '3':
            remote = input("  Remote blob path to download: ").strip()
            local = input("  Local path to save to: ").strip()
            if confirm(f"Download '{remote}' → '{local}'?"):
                try:
                    mgr.download_file(remote, local)
                except Exception as e:
                    print(f"  ❌ Download error: {e}")
                else:
                    print("  ✅ Download complete.")
            else:
                print("  ❌ Cancelled.")

        elif choice == '4':
            remote = input("  Remote blob path to delete: ").strip()
            if confirm(f"Delete blob '{remote}'?"):
                try:
                    mgr.delete_file(remote)
                except Exception as e:
                    print(f"  ❌ Delete error: {e}")
                else:
                    print("  ✅ Deletion complete.")
            else:
                print("  ❌ Cancelled.")

        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()
