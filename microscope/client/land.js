var logger = new Logger('Client:land');

Logger.setLevel('Client:land', 'trace');
// Logger.setLevel('Client:land', 'debug');
// Logger.setLevel('Client:land', 'info');
// Logger.setLevel('Client:land', 'warn');

Template.land.events({
    'click .continue' : function() {
        logger.debug("User clicked continue");
        // add logic here to make sure they are logged in
        var doc = DocumentManager.sampleDocument(); 
        logger.trace("Sending user to annotate document " + JSON.stringify(doc));
        Router.go("Annotate", {docID: doc._id});
    }
});