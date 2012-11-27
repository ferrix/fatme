function (doc) {
    if (doc.date == new Date().toISOString().split("T")[0]) {
        emit("today", doc.weight);
    }
}
