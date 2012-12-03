function(doc) {
    if (doc.doc_type == "Weight") {
        emit(doc.date, {doc_type: doc.doc_type, date: doc.date, weight: doc.weight, change: doc.weight});
    }
}
