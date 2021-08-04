FROM mongo

COPY test_forms.json /test_forms.json
CMD mongoimport --host db --db form_database --collection forms --type json --file /test_forms.json --jsonArray
