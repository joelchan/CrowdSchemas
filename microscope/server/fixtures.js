if (Posts.find().count() === 0) {
  Posts.insert({
    title: 'Introducing Telescope',
    url: 'http://sachagreif.com/introducing-telescope/'
  });

  Posts.insert({
    title: 'Meteor',
    url: 'http://meteor.com'
  });

  Posts.insert({
    title: 'The Meteor Book',
    url: 'http://themeteorbook.com'
  });
}

if (Documents.find().count() == 0) {
  // var doc = new Document("Dummy");
  // var docID = Documents.insert(doc);
  // SentenceFactory.createSentence(docID, "This is a sentence", 1);
  // SentenceFactory.createSentence(docID, "Another dummy sentence", 2);
  // SentenceFactory.createSentence(docID, "A third dummy sentence", 3);
  quirkyDocs.forEach(function(doc){
    DocumentManager.createDocument(doc);
  });
}