export class AccountSettingsController {
  
  userAccount;

  constructor(AppApi, $stateParams, $mdDialog, $mdToast, $state) {
  console.log($stateParams);
    this.AppApi = AppApi;
    this.$stateParams = $stateParams;
    this.$mdDialog = $mdDialog;
    this.$mdToast = $mdToast;
    this.$state = $state;
    this.userAccount = {};
  }

  $onInit() {

    if (this.$stateParams.accountId) {
      console.log("test");
      this.AppApi.getUserAccount(this.$stateParams.accountId)
        .then((successResponse) => {
          this.userAccount = successResponse.data;
        }, (errorResponse) => {
          this.userAccount = null;
        });
    } else {
      this.userAccount = null;
    }
  }

  goBack = function(){
        this.$state.go('accountList')
  }

  submitForm = function(){
        this.AppApi.submitForm({
		         'api_key': this.userAccount.api_key,
                 'user_integration': this.$stateParams.accountId,
                 'domain_name' : this.userAccount.domain_name
				      })
					  .then(function(response){
					    console.log("success");
					    this.userAccount.is_valid = response.data.is_valid;
					  	this.$mdToast.show(this.$mdToast.simple().textContent(response.data));
					  	if(response.data != "Invalid credentials. Please try again !")
					    this.$state.go('accountList')
					    }.bind(this) ,
					    function(response){
					        console.log("fail")
					        this.$mdToast.show(this.$mdToast.simple().textContent("Something went wrong, try again later"));
					    }.bind(this));
  }
//
//  addPage(){
//  console.log("adding pages")
//    this.userAccount.pages = [...this.userAccount.pages, ""];
//  }
//
//  deletePage(index){
//
//  if (this.userAccount.pages.length > 1){
//    this.userAccount.pages = this.userAccount.pages.slice(0,index).concat(this.userAccount.pages.slice(index+1,this.userAccount.pages.length))
//  }
//  console.log("deleting pages" + index)
//  }

  deleteAccount() {
  console.log("deleting");
    this.AppApi.deleteUserAccount(this.$stateParams.accountId)
      .then((successResponse) => {
        this.$state.go("accountList");
        this.$mdToast.show(this.$mdToast.simple().textContent('Your integration has been successfully removed'));
      }, (errorResponse) => {
        this.$mdToast.show(this.$mdToast.simple().textContent('Unable to remove your account at the moment'));
      });
  }

  onDeleteAccount() {
    var confirm = this.$mdDialog.confirm()
          .title("Would you like to remove this Mailgun integration with Yellowant?")
          .ariaLabel("mailgun Handle")
          .clickOutsideToClose(true)
          .ok('Delete Integration')
          .cancel('Cancel');

    this.$mdDialog.show(confirm).then(() =>
    {
      this.deleteAccount()
    }, function() { });
  }


  onDeleteWebhook(webhook) {
    var confirm = this.$mdDialog.confirm()
          .title(`Would you like to remove your webhook ${webhook.id} for "${webhook.repo_full_name}"?`)
          .clickOutsideToClose(true)
          .ok('Delete Webhook')
          .cancel('Cancel');

    this.$mdDialog.show(confirm).then(() =>
    {
      this.deleteWebhook(webhook);
    }, function() { });
  }

  deleteWebhook(webhook) {
    this.AppApi.deleteUserWebhook(this.$stateParams.accountId, webhook.id)
      .then((successResponse) => {
        this.$mdToast.show(this.$mdToast.simple().textContent('Deleted webhook successfully!'));
        webhook.is_deleted = true;
      }, (errorResponse) => {
        this.$mdToast.show(this.$mdToast.simple().textContent('Unable to delete the webhook at the moment'));
      });
  }


}

