import os
from dotenv import load_dotenv
from google.cloud import firestore

load_dotenv()

# Initialize Firestore client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT_KEY_PATH"
)
db = firestore.Client()


def add_document_array(
    collection_name, document_id, reference_name, new_item, unique_fields=None
):
    """
    Adds an item to an array in a Firestore document

    Args:
        collection_name: Name of the Firestore collection
        document_id: ID of the document
        reference_name: Field name containing the array
        new_item: New item to add to the array
        unique_fields: Optional list of fields to check for duplicates (e.g., ['user_name', 'email'])
    """
    try:
        doc_ref = db.collection(collection_name).document(document_id)
        doc = doc_ref.get()

        existing_items = doc.to_dict().get(reference_name, []) if doc.exists else []

        # Check for duplicates only if unique_fields is provided
        if unique_fields:
            for field in unique_fields:
                item_exists = any(
                    item[field] == new_item[field] for item in existing_items
                )
                if item_exists:
                    return False, f"Item with {field} already exists"

        # Add new item
        updated_items = existing_items + [new_item]
        doc_ref.set({reference_name: updated_items})
        return True, "Item successfully added"

    except Exception as error:
        return False, f"Error: {str(error)}"


def get_document_array(collection_name, document_id, reference_name, filters=None):
    """
    Get and filter array items from a Firestore document

    Args:
        collection_name: Name of the Firestore collection
        document_id: ID of the document
        reference_name: Field name containing the array
        filters: Optional dict of field-value pairs to filter the array (e.g., {'user_id': '123'})
    """
    try:
        doc_ref = db.collection(collection_name).document(document_id)

        doc = doc_ref.get()
        if doc.exists:
            doc_data = doc.to_dict()
            if doc_data and reference_name in doc_data:
                items = doc_data[reference_name]

                # Apply filters if provided
                if filters:
                    items = [
                        item
                        for item in items
                        if all(
                            field in item and item[field] == value
                            for field, value in filters.items()
                        )
                    ]

                return True, items
            else:
                return False, f"No items found in {reference_name}"
        else:
            return False, f"Document {document_id} does not exist in {collection_name}"
    except Exception as error:
        return False, f"Error: {str(error)}"



def get_paginated_stations_array(collection_name, document_id, reference_name, filters=None, limit=None, offset=0):
    """
    Get and filter array items from a Firestore document

    Args:
        collection_name: Name of the Firestore collection
        document_id: ID of the document
        reference_name: Field name containing the array
        filters: Optional dict of field-value pairs to filter the array (e.g., {'user_id': '123'})
        limit: Optional integer to limit the number of items returned
        offset: Optional integer to skip a number of items before starting to return results
    """
    try:
        doc_ref = db.collection(collection_name).document(document_id)

        doc = doc_ref.get()
        if doc.exists:
            doc_data = doc.to_dict()
            if doc_data and reference_name in doc_data:
                items = doc_data[reference_name]

                # Apply filters if provided
                if filters:
                    items = [
                        item
                        for item in items
                        if all(
                            field in item and item[field] == value
                            for field, value in filters.items()
                        )
                    ]

                # Apply offset and limit for pagination
                if offset:
                    items = items[offset:]  # Skip the first 'offset' items
                if limit is not None:
                    items = items[:limit]  # Limit the number of items returned

                return True, items
            else:
                return False, f"No items found in {reference_name}"
        else:
            return False, f"Document {document_id} does not exist in {collection_name}"
    except Exception as error:
        return False, f"Error: {str(error)}"


def get_paginated_users_array(collection_name, document_id, reference_name, filters=None, limit=None, offset=0):
    """
    Get and filter array items from a Firestore document

    Args:
        collection_name: Name of the Firestore collection
        document_id: ID of the document
        reference_name: Field name containing the array
        filters: Optional dict of field-value pairs to filter the array (e.g., {'user_id': '123'})
        limit: Optional integer to limit the number of items returned
        offset: Optional integer to skip a number of items before starting to return results
    """
    try:
        doc_ref = db.collection(collection_name).document(document_id)

        doc = doc_ref.get()
        if doc.exists:
            doc_data = doc.to_dict()
            if doc_data and reference_name in doc_data:
                items = doc_data[reference_name]

                # Apply filters if provided
                if filters:
                    items = [
                        item
                        for item in items
                        if all(
                            field in item and item[field] == value
                            for field, value in filters.items()
                        )
                    ]

                # Apply offset and limit for pagination
                if offset:
                    items = items[offset:]  # Skip the first 'offset' items
                if limit is not None:
                    items = items[:limit]  # Limit the number of items returned

                return True, items
            else:
                return False, f"No items found in {reference_name}"
        else:
            return False, f"Document {document_id} does not exist in {collection_name}"
    except Exception as error:
        return False, f"Error: {str(error)}"









def update_document_array(
    collection_name, document_id, reference_name, updated_item, unique_fields=None
):
    try:
        doc_ref = db.collection(collection_name).document(document_id)
        doc = doc_ref.get()

        existing_items = doc.to_dict().get(reference_name, []) if doc.exists else []
        item_exists = False
        item_index = -1

        if unique_fields:
            # Find item to update by checking unique fields
            for i, item in enumerate(existing_items):
                for field in unique_fields:
                    if item[field] == updated_item[field]:
                        item_exists = True
                        item_index = i
                        break
                if item_exists:
                    break

            # Check for conflicts with other items
            if item_exists:
                for field in unique_fields:
                    for i, item in enumerate(existing_items):
                        if (
                            i != item_index  # Skip the item being updated
                            and field in updated_item
                            and item[field] == updated_item[field]
                        ):
                            return False, f"Another item with {field} already exists"

        if item_exists:
            # Update the item if found
            existing_items[item_index] = {**existing_items[item_index], **updated_item}
            message = f"Item successfully updated in {reference_name}"
        else:
            # If no unique fields or item not found, append as new item
            existing_items.append(updated_item)
            message = f"Item successfully added to {reference_name}"

        doc_ref.set({reference_name: existing_items})
        return True, message

    except Exception as error:
        return False, f"Error: {str(error)}"


def delete_document_array_item(
    collection_name, document_id, reference_name, unique_fields=None, unique_values=None
):
    """
    Args:
        unique_fields: Optional list of fields to identify the item
        unique_values: Optional list of values corresponding to unique_fields
    """
    try:
        # Input validation
        if not unique_fields or not unique_values:
            return False, "Unique fields and values are required for deletion"

        if len(unique_fields) != len(unique_values):
            return False, "Number of unique fields must match number of values"

        doc_ref = db.collection(collection_name).document(document_id)
        doc = doc_ref.get()

        if not doc.exists:
            return False, f"Document {document_id} does not exist"

        doc_data = doc.to_dict()
        if not doc_data or reference_name not in doc_data:
            return False, f"No items found in {reference_name}"

        existing_items = doc_data[reference_name]
        original_length = len(existing_items)

        # Filter out the item that matches ALL unique fields
        updated_items = [
            item
            for item in existing_items
            if not all(
                field in item and item[field] == value
                for field, value in zip(unique_fields, unique_values)
            )
        ]

        if len(updated_items) == original_length:
            return False, "Item not found"

        # Update the document with the filtered array
        doc_ref.set({reference_name: updated_items}, merge=True)
        return True, f"Item successfully deleted from {reference_name}"

    except Exception as error:
        return False, f"Error: {str(error)}"
