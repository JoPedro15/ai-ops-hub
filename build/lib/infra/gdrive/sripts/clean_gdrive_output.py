import os
from pathlib import Path

from clients.core_lib.core_lib_client.logger_client import logger
from clients.gdrive.gdrive_client.client import GDriveClient
from dotenv import load_dotenv


def main() -> None:
    """
    Performs a safe cleanup of the Google Drive output folder.
    Moves ALL files inside the target folder to the Trash.
    """
    load_dotenv()

    root: Path = Path(__file__).parent.parent
    creds_path: str = str(root / "data" / "credentials.json")
    token_path: str = str(root / "data" / "token.json")

    output_id: str = os.getenv("OUTPUT_FOLDER_ID", "")

    if not output_id:
        logger.error("OUTPUT_FOLDER_ID not found in environment variables.")
        return

    client: GDriveClient = GDriveClient(
        credentials_path=creds_path, token_path=token_path
    )

    logger.info(f"Starting SAFE cleanup (Trash) in output folder (ID: {output_id})")

    # 1. Get all files in the folder
    files_to_trash: list[dict[str, str]] = client.list_files(
        folder_id=output_id,
        limit=1000,
    )

    if not files_to_trash:
        logger.info("Folder is already empty. No action needed.")
        return

    logger.warning(f"Found {len(files_to_trash)} items. Moving to Trash...")

    # 2. Update files to set 'trashed' to True
    trashed_ids: list[str] = []
    for f in files_to_trash:
        file_name: str = f.get("name", "Unknown Name")
        file_id: str = f.get("id", "Unknown ID")

        try:
            logger.warning(f"Trashing: {file_name} (ID: {file_id})")

            # Using update instead of delete for safety
            client.service.files().update(
                fileId=file_id, body={"trashed": True}
            ).execute()

            trashed_ids.append(file_id)

        except Exception as e:
            logger.error(f"Failed to trash {file_name}: {e}")

    # Final Execution Report
    if trashed_ids:
        logger.success(
            f"Cleanup complete! Moved {len(trashed_ids)} items to the Trash."
        )


if __name__ == "__main__":
    main()
