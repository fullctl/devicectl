(function($, $tc, $ctl) {

$ctl.application.Devicectl = $tc.extend(
  "Devicectl",
  {
    Devicectl : function() {
      this.Application("devicectl");

      this.urlkeys = {}
      this.exchanges = {}
      this.initial_load = false

      this.$c.header.app_slug = "device";

      $($ctl).trigger("init_tools", [this]);
    }
  },
  $ctl.application.Application
);


$(document).ready(function() {
  $ctl.devicectl = new $ctl.application.Devicectl();
});

})(jQuery, twentyc.cls, fullctl);
