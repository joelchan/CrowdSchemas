Template.annotationPage.helpers({
    thisDoc: function() {
        return Documents.find();
    }
});

Template.document.helpers({
    sentences: function() {
        return Sentences.find({docID: this._id});
    }
});

Template.sentence.helpers({
    words: function() {
        return Words.find({sentenceID: this._id});
    }
})

Template.word.events({
    'click .token': function(event, target) {
        t = target.firstNode;
        tID = "#" + t.id;
        console.log("clicked on " + tID);
        $(tID).toggleClass('highlight-problem');
    }
})