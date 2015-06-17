Template.annotationPage.helpers({
    sentences: function() {
        return Sentences.find({docID: this._id});
    }
});

Template.sentence.helpers({
    words: function() {
        return Words.find({sentenceID: this._id});
    }
});

Template.word.helpers({
    isProblem: function() {
        // stub code for now, return true if the user
        // has marked this word as a problem word
        return true;
    },
    isMech: function() {
        // stub code for now, return true if the user
        // has marked this word as a solution word
        return true;
    }
});

Template.word.events({
    'click .key-option': function(event) {
        var selection = event.currentTarget;
        // var keyType = selection.innerText;
        console.log(selection);
        var word = selection.parentNode.previousElementSibling;
        console.log(word);
        var wordID = "#" + word.id;
        console.log("clicked on " + wordID);
        if (selection.classList.contains("prob")) {
            console.log("It's a problem!");
            $(wordID).addClass('highlight-problem');
            $(wordID).removeClass('highlight-mechanism');
        } else if (selection.classList.contains("mech")) {
            console.log("It's a mechanism!");
            $(wordID).removeClass('highlight-problem');
            $(wordID).addClass('highlight-mechanism');
        } else {
            console.log("It's neither!");
            $(wordID).removeClass('highlight-problem');
            $(wordID).removeClass('highlight-mechanism');
        }
        
    }
})