function(doc) {
    if (doc.doc_type == "Start") {
        emit("s"+doc.date, {doc_type: doc.doc_type,
                            final_day: doc.final_day,
                            goal: doc.goal,
                            height: doc.height,
                            age: doc.age,
                            name: doc.name,
                            picture: doc.picture
                           });
    }
}
