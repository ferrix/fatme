function(doc) {
    if (doc.doc_type == "Weight")
        emit(doc.date, doc);
}
