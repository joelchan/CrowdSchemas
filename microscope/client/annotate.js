var logger = new Logger('Client:annotate');

Logger.setLevel('Client:annotate', 'trace');
// Logger.setLevel('Client:annotate', 'debug');
// Logger.setLevel('Client:annotate', 'info');
// Logger.setLevel('Client:annotate', 'warn');

Template.annotationPage.helpers({
    isLoggedIn: function() {
        var user = Meteor.user();
        if (user) {
            return true;
        } else {
            return false;
        }
    }
});

Template.annotateTask.helpers({
    sentences: function() {
        return Sentences.find({docID: Session.get("currentDoc")._id});
    }
});

Template.annotateTask.events({
    'click .another': function() {
        do { 
            var doc = DocumentManager.sampleDocument();
        }
        while (doc._id === Session.get("currentDoc")._id);
        Session.set("currentDoc", doc);
    },
    'click .finished': function() {
        Router.go("Finish");
    }
})

Template.sentence.helpers({
    words: function() {
        return Words.find({sentenceID: this._id});
    }
});

Template.word.helpers({
    isPurpose: function() {
        var userID = Meteor.user()._id;
        // logger.debug("Current user is " + userID);
        // logger.trace("Users who have higlighted this as a purpose keyword: " + 
            // JSON.stringify(this.highlightsPurpose));
        if (isInList(userID, this.highlightsPurpose)) {
            // logger.debug("isPurpose is true");
            return true;    
        } else {
            return false;
        }
    },
    isMech: function() {
        var userID = Meteor.user()._id;
        // logger.debug("Current user is " + userID);
        // logger.trace("Users who have higlighted this as a mechanism keyword: " + 
            // JSON.stringify(this.highlightsMechanism));
        if (isInList(userID, this.highlightsMechanism)) {
            // logger.debug("isMech is true");
            return true;    
        } else {
            return false;
        }
    },
    isNeutral: function() {
        var userID = Meteor.user()._id;
        if (!isInList(userID, this.highlightsPurpose) &&
            !isInList(userID, this.highlightsMechanism)) {
            // logger.debug("isNeutral is true");
            return true;    
        } else {
            return false;
        }
    }
});

Template.word.events({
    'click .key-option': function(event) {
        var selection = event.currentTarget;
        // var keyType = selection.innerText;
        // console.log(selection);
        var word = selection.parentNode.previousElementSibling;
        // console.log(word);
        var wordID = trimFromString(word.id, "word-");
        var userID = Meteor.user()._id;
        logger.trace(userID + " clicked on " + wordID);
        if (selection.classList.contains("purp")) {
            WordManager.markWord(wordID, userID, "Purpose");
        } else if (selection.classList.contains("mech")) {
            WordManager.markWord(wordID, userID, "Mechanism");
        } else {
            WordManager.markWord(wordID, userID, "Neither");
        }
    }
})