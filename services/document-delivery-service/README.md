## Builder

test run

# service_http



```bash
docker build -t gcr.io/doc-gent/document-generation-service .
```
```bash
docker run --rm -p 8080:8080 gcr.io/doc-gent/document-generation-service
```

No data element
```bash
curl -i -X POST  http://0.0.0.0:8080/ \
-H "Content-Type: text/text" \
--data-binary '{"datacontenttype": "application/json", "id": "3f25e888-0166-45aa-ae5d-eb2c695e635f", "source": null, "specversion": "1.0", "subject": null, "time": "2021-12-19T23:49:06.082250+00:00", "type": null}'
```

With a data element
```bash
curl -i -X POST  http://0.0.0.0:8080/ \
-H "Content-Type: text/text" \
--data-binary '{"datacontenttype": "application/json", "id": "3f25e888-0166-45aa-ae5d-eb2c695e635f", "source": null, "specversion": "1.0", "subject": null, "time": "2021-12-19T23:49:06.082250+00:00", "type": null, "data": {"docId": "123abc"}}'
```
