var logger = new Logger('Client:tutorial');

Logger.setLevel('Client:tutorial', 'trace');
// Logger.setLevel('Client:tutorial', 'debug');
// Logger.setLevel('Client:tutorial', 'info');
// Logger.setLevel('Client:tutorial', 'warn');

Template.tutorialSentence.helpers({
    sampleWords : function() {
        var sentence = "Just remove the base to easily switch between straining and serving functions, and save yourself from washing more dirty dishes!"
        var words = sentence.split(" ");
        var wordObjects = [];
        for (i=0; i < words.length; i++) {
            var w = {_id: i, content: words[i]}
            wordObjects.push(w);
        }
        logger.trace("Tutorial words: " + JSON.stringify(wordObjects))
        return wordObjects;
    }
});

Template.tutorialSentence.events({
    'click .key-option': function(event) {
        var selection = event.currentTarget;
        // var keyType = selection.innerText;
        // console.log(selection);
        var word = selection.parentNode.previousElementSibling;
        // console.log(word);
        var wordID = "#" + word.id;
        userID = Meteor.user()._id;
        logger.trace(userID + " clicked on " + wordID);
        if (selection.classList.contains("purp")) {
            $(wordID).addClass('key-purpose');
            $(wordID).removeClass('key-mechanism');
            $(wordID).removeClass('key-neutral');
        } else if (selection.classList.contains("mech")) {
            $(wordID).removeClass('key-purpose');
            $(wordID).addClass('key-mechanism');
            $(wordID).removeClass('key-neutral');
        } else {
            $(wordID).removeClass('key-purpose');
            $(wordID).removeClass('key-mechanism');
            $(wordID).addClass('key-neutral');
        }
    }
});

Template.tutorial.events({
    'click .continue' : function() {
        logger.debug("User clicked continue");

        if (Meteor.user()) {
            var doc = DocumentManager.sampleDocument(); 
            logger.trace("Sending user to annotation task with document " + JSON.stringify(doc));
            Router.go("Annotate", {docID: doc._id});    
        } else {
            alert("Please log in or create an account before continuing");
        }   
    }
});