## Search Tester Next Steps

### import 'legacy' searches differently
Update this cronjob to grab recent searches from the active application in PROD.
- alter *get_batch_searches_table* to get data from active *search_requests/search_results* tables and insert data accordingly
- alter *add_legacy_results* to insert new data set (will now be identical to *add_api_results* probably except for the SOURCE value)

Setup cronjob to run every day

### Notebook
- no changes

### api structure
- no changes

### nice to have
Could add endpoints to the api for the test tables and a simple UI that makes viewing the data super easy. This would eliminate the need for the notebook as you would essentially just add everything the notebook does into a simple UI for staff / testers that's much easier to visualize. You would only need the UI active in DEV