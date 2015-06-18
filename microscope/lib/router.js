Router.configure({
  layoutTemplate: 'layout',
  loadingTemplate: 'loading',
  waitOn: function() { 
    return [
        Meteor.subscribe('posts'),
        // Meteor.subscribe('documents'),
        // Meteor.subscribe('sentences'),
        // Meteor.subscribe('words')
    ];
  }
});

Router.map(function() {
    
    // this.route('/', {name: 'postsList'});

    this.route('/posts/:_id', {
        name: 'postPage',
        data: function() { return Posts.findOne(this.params._id); }
    });

    this.route('Land', {
        name: 'Land',
        path: '/',
        template: 'land',
        subscriptions: function()  {
            this.subscribe("documents");
        },
        onBeforeAction: function() {
            if (this.ready()) {
                $('.navbar-brand').text("Annotator: Welcome");    
                this.next();
            }
        }
    });

    this.route('Tutorial', {
        name: 'Tutorial',
        path: '/tutorial/',
        template: 'tutorial',
        subscriptions: function() {
            this.subscribe("documents");
        },
        onBeforeAction: function() { 
            if(this.ready()) {
                $('.navbar-brand').text("Annotator: Welcome >> Tutorial");
                this.next();
            }
        },
    });

    this.route('Annotate', {
        name: 'Annotate',
        path: '/annotate/:docID',
        template: 'annotationPage',
        subscriptions: function() {
            this.subscribe("documents", {_id: this.params.docID});
            this.subscribe("summaries");
            this.subscribe("sentences", {docID: this.params.docID});
            this.subscribe("words", {docID: this.params.docID});
        },
        onBeforeAction: function() { 
            if(this.ready()) {
                // var doc = DocumentManager.sampleDocument();
                var doc = Documents.findOne({_id: this.params.docID});
                Session.set("currentDoc", doc);
                $('.navbar-brand').text("Annotator: Welcome >> Tutorial >> Main Task");
                this.next();
            }
        },
    })

    this.route('Finish', {
        name: 'Finish',
        path: '/finish/',
        template: 'finishPage',
        onBeforeAction: function() { 
            if(this.ready()) {
                $('.navbar-brand').text("Annotator: Welcome >> Tutorial >> Main Task >> Finish");
                this.next();
            }
        },
    })

})