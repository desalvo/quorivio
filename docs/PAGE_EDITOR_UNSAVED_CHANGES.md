# Unsaved editor changes

The full-page editor detects local unsaved changes to widgets, headers, and question/results backgrounds. Switching thumbnails or closing the editor requests confirmation; a browser refresh/tab close also triggers the native before-unload warning. The successful PATCH resets the dirty baseline.

There is no autosave; browser end-to-end behavior remains to be validated.
