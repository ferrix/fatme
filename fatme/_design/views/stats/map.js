function(doc) {
    if (doc.doc_type == "Weight")
    {
        emit(doc.doc_type, doc.weight);
    }
}
