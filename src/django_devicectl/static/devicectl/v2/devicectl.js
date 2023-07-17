(function ($, $tc, $ctl) {

$ctl.application.Devicectl = $tc.extend(
  "Devicectl",
  {
    Devicectl: function () {
      this.Application("devicectl");

      this.urlkeys = {}
      this.facilities = {}
      this.facility_slugs = {}
      this.initial_load = false

      this.init_container("facility", "facilities");

      this.$c.header.app_slug = "device";

      this.tool("dashboard", () => {
        return new $ctl.application.Devicectl.DeviceDashboard();
      })

      this.tool("devices", () => {
        return new $ctl.application.Devicectl.Devices();
      });

      this.tool("device", () => {
        return new $ctl.application.Devicectl.DeviceDetails();
      });

      this.tool("logical_ports", () => {
        return new $ctl.application.Devicectl.LogicalPorts();
      });

      this.tool("physical_ports", () => {
        return new $ctl.application.Devicectl.PhysicalPorts();
      });

      this.tool("virtual_ports", () => {
        return new $ctl.application.Devicectl.VirtualPorts();
      });

      $(this.$c.toolbar.$e.button_create_facility).click(() => {
        fullctl.devicectl.page('facilities');
        fullctl.devicectl.$t.settings.create_facility();
      });
      $(this.$c.toolbar.$e.return_to_dashboard).click(() => {
        fullctl.devicectl.page("dashboard");
      });

      $(this).one("no-containers", () => {
        fullctl.devicectl.page('facilities');
        fullctl.devicectl.$t.settings.create_facility();
      });



      this.$c.toolbar.widget("select_device", ($e) => {
        var e = $e["select_device"];

        var w = new twentyc.rest.Select(e);

        w.format_request_url = (url) => {
          return url.replace(/facility_tag/g, this.facility_slug());
        };

        $(w).on("load:after", (event, element, data) => {

          if(!data.length) {
            $('.no-devices').show();
            $('.device-container').hide();
          } else {
            $('.no-devices').hide();
            $('.device-container').show();
            this.$t.virtual_ports.sync();
            this.$t.logical_ports.sync();
            this.$t.physical_ports.sync();
            this.$t.device.show_device(e.val());
          }

        });


        $(w.element).on("change", (event, element, data) => {

          this.$t.virtual_ports.sync();
          this.$t.logical_ports.sync();
          this.$t.physical_ports.sync();
          this.$t.device.show_device(e.val());

        });

        return w;
      });

      $(this.$c.toolbar.$w.select_facility).on("load:after", () => {
        this.$c.toolbar.$w.select_device.load().then(() => {
        });
      });

      $(this.$c.toolbar.$w.select_facility.element).on("change", () => {
        this.$c.toolbar.$w.select_device.load().then(() => {
        });
      });


      $('#ports-tab').on('show.bs.tab', () => {
        this.$c.toolbar.$e.select_device_toggle.show();
        this.$c.toolbar.$w.select_device.load();
      });
      $('#ports-tab').on('hide.bs.tab', () => { this.$c.toolbar.$e.select_device_toggle.hide(); });

      // dont show facility selection toolbar in dashboard
      // TODO: move toolbar to be tabbed 

      $('#dashboard-tab').on('show.bs.tab', () => {
        $('#facility-select-toolbar').hide();
        this.$t.dashboard.sync();
      });
      $('#dashboard-tab').on('hide.bs.tab', () => {
        $('#facility-select-toolbar').show();
      });

      $('#ports-tab').on('show.bs.tab', () => {
        $('[data-element=button_create_facility]').hide();
        $('[data-component=virtual_ports').appendTo($("#device-detail"));
        $('[data-component=logical_ports').appendTo($("#device-detail"));
        $('[data-component=physical_ports').appendTo($("#device-detail"));
      });

      $('#tab-overview').on('show.bs.tab', () => {
        $('[data-element=button_create_facility]').show();
      });

      $($ctl).trigger("init_tools", [this]);

      this.$t.devices.activate();
      this.$t.logical_ports.activate();
      this.$t.physical_ports.activate();
      this.$t.virtual_ports.activate();

      this.sync();

      this.autoload_page();
    },

    page: function(page) {
      switch(page) {
        case "device-details":
        case "changes":
        case "current-config":
        case "reference-config":
        case "history":
          page = "ports";
      }  

      this.ContainerApplication_page(page);
    },

    device_id: function () {
      if (!this.$c.toolbar.$e.select_device) {
        return null;
      }

      return this.$c.toolbar.$w.select_device.element.val();

    },

    device_name: function () {
      if (!this.$c.toolbar.$e.select_device) {
        return null;
      }

      return this.$c.toolbar.$w.select_device.element.find('option:selected').text();

    },
    
    permission_ui: function () {
      //let $e = this.$c.toolbar.$e;
      //let facility = this.facilities[this.facility()];
      //let org = $ctl.org.id;
      //$e.button_create_facility.grainy_toggle(`facility.${org}`, "c");
      //$e.button_import_facility.grainy_toggle(`facility.${org}`, "c");
    }

  },
  $ctl.application.ContainerApplication
);

/**
 * Extended twentyc.rest list widget that will render a device
 * dashboard of device tiles, showing devices that are currently
 * showing operational issues
 * 
 * @class $ctl.application.Devicectl.DeviceDashboard
 * @extends $ctl.application.Tool
 * @namespoace $ctl.application.Devicectl
 * @constructor
 */

$ctl.application.Devicectl.DeviceDashboard = $tc.extend(
  "DeviceDashboard",
  {
    DeviceDashboard: function () {
      this.Tool("device_dashboard");
    },

    init: function() {
      this.widget("list", ($e) => {
        return new twentyc.rest.List(
          this.template("list", this.$e.body)
        );
      });

      this.$w.list.formatters.row = (row, data) => {
        if(data.operational_status == "error") {
          row.addClass("badge bg-danger");
        }

        row.click(() => {
          
          $(fullctl.devicectl.$c.toolbar.$w.select_device).one("load:after", ()=> {
            fullctl.devicectl.$c.toolbar.$w.select_device.element.val(data.id);
          })
          
          if(data.facility != parseInt(fullctl.devicectl.facility())) {

            fullctl.devicectl.select_facility(data.facility);
            
          } 

          fullctl.devicectl.page("ports");
        })
      };

      this.sync();
    },

    sync : function() {
      if (!$ctl.devicectl) {
        return;
      }
      let namespace = `device.${$ctl.org.id}`
      if (!grainy.check(namespace, "r")) {
        return;
      }
      this.$w.list.load();
    }
  },
  $ctl.application.Tool
);

/**
 * Config loader widget
 * 
 * @class ConfigLoader
 * @extends twentyc.rest.widget
 * @namespace twentyc.rest
 * @constructor
 */


$ctl.application.Devicectl.ConfigLoader = $tc.extend(
  "ConfigLoader",
  {
    ConfigLoader: function(jq) {
      var base_url = jq.data("api-base");
      this.Widget(base_url, jq);
    },

    bind : function(jq) {
      this.Widget_bind(jq);
      this.config_content = jq.find(".config-content")
      this.button_raw = jq.find("[data-element=button_raw]")
      this.button_source = jq.find("[data-element=button_source]")
      this.syntax_highlight = this.config_content.data("syntax-highlight")
    },

    /**
     * loads config
     *
     * triggers load:after event
     *
     * @method load
     */

    load : function() {
      this.config_content.empty();
      return this.get(this.action, this.payload()).then(function(response) {
        let config = response.first();
        if(!config)
          return;
          
        let code_block = $("<pre>").addClass("language-diff").text(config.config);
        this.config_content.append(code_block);

        if(this.syntax_highlight) {
          hljs.highlightBlock(code_block[0]);
        }

        this.button_raw.attr("href", this.format_request_url(this.base_url) + "/plain");
        this.button_source.attr("href", config.url);
      }.bind(this));
    },
  },
  twentyc.rest.Widget
);

/**
 * Device details tool
 */

$ctl.application.Devicectl.DeviceDetails = $tc.extend(
  "DeviceDetails",
  {
    DeviceDetails: function () {
      this.Tool("device_details");
      this.device_id = 0;
      this.config_history_loaded = false;

      $("#deviceStatusTabs")
    },

    init : function() {

      // create device details widget that holds device kind, facility, sessions and events

      this.widget("device", ($e) => {
        return new twentyc.rest.Form(
          this.template("device_widget", this.$e.device_container)
        );
      });

      // create operational status widget (will show error message if status is error)

      this.widget("operational_status", ($e) => {
        return new twentyc.rest.Form(
          this.template("device_operational_status", this.$e.operational_status_container)
        );
      });

      // create config history listing widget

      this.widget("config_history", ($e) => {
        return new twentyc.rest.List(
          this.template("device_config_history", this.$e.config_history_container)
        )
      });

      // create config changes widget

      this.widget("config_changes", ($e) => {
        return new $ctl.application.Devicectl.ConfigLoader(
          this.template("device_config_changes", this.$e.config_changes_container)
        )
      });

      // create current config widget

      this.widget("current_config", ($e) => {
        return new $ctl.application.Devicectl.ConfigLoader(
          this.template("device_current_config", this.$e.current_config_container)
        )
      });

      // create reference config widget

      this.widget("reference_config", ($e) => {
        return new $ctl.application.Devicectl.ConfigLoader(
          this.template("device_reference_config", this.$e.reference_config_container)
        )
      });

      // url formatting to replace /0/ with /<device_id>/ across
      // all widgets

      this.$w.config_changes.format_request_url = (url) => {
        return url.replace("/0/", "/"+this.device_id+"/");
      };

      this.$w.current_config.format_request_url = (url) => {
        return url.replace("/0/", "/"+this.device_id+"/");
      };

      this.$w.reference_config.format_request_url = (url) => {
        return url.replace("/0/", "/"+this.device_id+"/");
      };
      
      this.$w.config_history.format_request_url = (url) => {
        return url.replace("/0/", "/"+this.device_id+"/");
      };

      // set up config history listing widget

      this.$w.config_history.formatters.error_message = (value, data) => {
        if(value) {
          return $("<div class='text-danger'>").text(value);
        }
        return value;
      };
      // format status to be a badge

      this.$w.config_history.formatters.status = (value, data) => {
        let badge = $("<span>").addClass("badge");
        if(data.status=="ok") {
          badge.addClass("bg-success");
        } else if(data.status=="error") {
          badge.addClass("bg-danger");
        }
        return badge.text(data.status);
      };

      this.$w.config_history.formatters.created = fullctl.formatters.datetime;

      // upon showing the config history tab, load the config history
      // if it has not been loaded yet
      $('#history-tab').on('show.bs.tab', () => {
        this.$w.config_history.load().then(() => {this.config_history_loaded = true;})
      });

      // upon showing the changes tab, load the config changes diff
      $('#changes-tab').on('show.bs.tab', () => {
        this.$w.config_changes.load();
      });

      // upon showing the current-config tab, load the current config
      $('#current-config-tab').on('show.bs.tab', () => {
        this.$w.current_config.load();
      });
      
      // upon showing the reference-config tab, load the reference config
      $('#reference-config-tab').on('show.bs.tab', () => {
        this.$w.reference_config.load();
      });

    },

    show_device : function(device_id) {

      this.device_id = device_id;
      this.config_history_loaded = false;

      this.$w.device.get(""+device_id).then(
        (response) => {
          let device = response.first();
          this.$e.menu.find('.device-name').text(device.display_name);
          this.$e.menu.find('.operational-status').text(
            device.operational_status == "error" ? "Issues" : "Ok"
          ).addClass(
            device.operational_status == "error" ? "bg-danger" : "bg-success"
          ).removeClass(
            device.operational_status == "error" ? "bg-success" : "bg-danger"
          );
          this.$w.device.fill(device);
          //$("#device-detail-tab").tab("show");
          
          this.render_service_links(device);
          this.show_graph_controls(device);
          this.show_graph(device);
        }
      )

      this.$w.operational_status.get(device_id+"/operational_status").then(
        (response) => {

          // 200 response, check device operational status

          let status = response.first();
          
          if(status.status == "error")
            this.$w.operational_status.element.find('.error-message').show();
          else 
            this.$w.operational_status.element.find('.error-message').hide();

          this.$w.operational_status.fill(status);

        },
        () => {

          // fail response (404 when device has never had operational status set, for now just assume device is ok)

          this.$w.operational_status.element.find('.error-message').hide();
          this.$w.operational_status.fill({
            status: "ok"
          });

        }
      )
    },

    /**
     * Will render relevant service links (like peerctl session overview)
     * 
     * This is called automatically when the device is loaded
     * @method render_service_links
     */

    render_service_links: function(device) {
      // first we check if the app link to peerctl exists for the user
      // by finding a[data-slug=peerctl]

      let $peerctl_link = $('a[data-slug=peerctl]').attr('href');
      let $auditctl_link = $('a[data-slug=auditctl]').attr('href');

      let facility_slug = device.facility_slug;
      let device_id = device.id;
      let device_name = device.name;

      if($peerctl_link) {
        this.$w.device.element.find('[data-field="peerctl_sessions_url"]').empty().append(
          $('<a>').attr('href', $peerctl_link + `#page-summary-sessions;${facility_slug};${device_id};;`).append(
            $('<img>').attr('src', `${fullctl.static_path}common/logos/peerctl-dark.svg`).addClass("service-link")
          ).append(
            $('<span class="icon icon-logout">')
          )
        )
        this.$w.device.element.find('.peerctl-link').show();
      } else {
        this.$w.device.element.find('.peerctl-link').hide();
      }

      if($auditctl_link) {
        this.$w.device.element.find('[data-field="auditctl_events_url"]').empty().append(
          $('<a>').attr('href', $auditctl_link + `/?q=config/device/${device_name}`).append(
            $('<img>').attr('src', `${fullctl.static_path}common/logos/auditctl-dark.svg`).addClass("service-link")
          ).append(
            $('<span class="icon icon-logout">')
          )
        )
        this.$w.device.element.find('.auditctl-link').show();
      } else {
        this.$w.device.element.find('.auditctl-link').hide();
      }
    },

    // Function to indicate loading
    indicate_loading : function() {
      let graph_container = this.$w.device.element.find("[data-element=graph_container]");
      console.log("LOADING GRAPH", graph_container.length, fullctl.template("graph_placeholder"))
      graph_container.empty().append(
        fullctl.template("graph_placeholder")
      );
      return this;
    },  

    show_graph_controls(device) {
      let node = this.$w.device.element;
      fullctl.graphs.init_controls(node, this, (end_date, duration)=>{
        this.indicate_loading().show_graph(device, end_date, duration);
      });
      node.find('.graph-controls').show();
      return this;
    },

    // Function to show graphs
    show_graph : function(device, end_date, duration) {
      let graph_container = this.$w.device.element.find("[data-element=graph_container]");
      let url = twentyc.rest.url.url_join(
        this.$w.device.element.data('api-base'),
        device.id,
        "traffic"
      );
      let params = [];
      if (end_date) {
        params.push('start_time=' + end_date);
      }
      if (end_date && duration) {
        params.push('duration=' + duration);
      }
      if (params.length > 0) {
        url += '?' + params.join('&');
      }
      fullctl.graphs.render_graph_from_file(
        url,
        ".graph_container",
        device.display_name,
      ).then(() => {
        // check if a svg has been added to the container, if not, graph data was empty
        if(graph_container.find("svg").length == 0) {
          graph_container.empty().append(
            $('<div class="alert alert-info">').append(
              $('<p>').text("No traffic data available for this device.")
            )
          )
        } else {
          this.$e.refresh_traffic_graph.show();
        }
      })
    }

  },
  $ctl.application.Tool
);

$ctl.application.Devicectl.Devices = $tc.extend(
  "Devices",
  {
    Devices: function () {
      this.sot = false;
      this.Tool("devices");
    },

    init: function () {

      this.delete_selected_button = this.$t.button_delete_selected;

      this.widget("list", ($e) => {
        return new $ctl.widget.SelectionList(
          this.template("list", this.$e.body),
          this.delete_selected_button
        );
      })

      this.$w.list.format_request_url = (url) => {
        if (!$ctl.devicectl)
          return url;
        return url.replace(/facility_tag/, $ctl.devicectl.facility_slug());
      }

      this.$w.list.formatters.facility_name = (value, data) => {
        if (!value)
          return "-";
        return value;
      };

      this.$w.list.formatters.row = (row, data) => {

        if (data.reference_is_sot && data.reference && data.reference_source) {
          row.find('[data-sot=external]').show();
          row.find("[data-action=link_to_reference]").attr("href", data.reference_ux_url);
        } else {
          row.find('[data-sot=devicectl]').show();
        }


        row.find('a[data-action="edit_device"]').click(() => {
          var device = row.data("apiobject");
          new $ctl.application.Devicectl.ModalDevice(device);
        }).each(function () {
          if (!grainy.check(data.grainy + ".?", "u")) {
            $(this).hide()
          }
        });

        let view_api_btn = row.find('a[data-action="view_api"]');
        view_api_btn.click(() => {
          let device = row.data("apiobject");
          window.open($(view_api_btn).attr("data-api-url").replace("0", device.id) + "?pretty");
        })

        if (!grainy.check(data.grainy, "d")) {
          row.find('a[data-api-method="DELETE"]').hide();
        }
      };

      this.initialize_sortable_headers("name");

      $(this.$w.list).on("api-request:error", () => {
        this.$w.list.list_body.empty();
      });

      $(this.$w.list).on("api_callback_remove:after", () => {
        $ctl.devicectl.sync();
      });
    },

    menu: function () {
      var menu = this.Tool_menu();
      menu.find('[data-element="button_add_device"]').click(() => {
        if (this.sot) {
          return new $ctl.application.Devicectl.ModalDevice();
        } else {
          return new $ctl.application.Devicectl.ModalAssignDevice();
        }
      });

      // v2 - insert delete selected button
      $(this.delete_selected_button).insertBefore(menu.find('[data-element="button_add_device"]'));

      $(this.delete_selected_button).click(() => {
        if (confirm("Remove selected Devices?")) {
          this.$w.list.delete_selected_list();
        }
      });

      return menu;
    },

    sync: function () {
      if (!$ctl.devicectl) {
        return;
      }
      let namespace = `device.${$ctl.org.id}`
      if (grainy.check(namespace, "r")) {
        this.show();
        this.apply_ordering();
        this.$w.list.load();

        var facility_tag = ($ctl.devicectl ? $ctl.devicectl.facility_slug() : '')

        // v2 - set up view API button
        this.$e.bottom_menu.find('[data-element="button_api_view"]').attr(
          "href", this.$w.list.base_url.replace(/facility_tag/g, facility_tag) + "/" + this.$w.list.action + "?pretty"
        )

        this.$e.menu.find('[data-element="button_add_device"]').grainy_toggle(namespace, "c")

      } else {
        this.hide();
      }
    }
  },
  $ctl.application.Tool
);

$ctl.application.Devicectl.ModalAssignDevice = $tc.extend(
  "ModalDevice",
  {
    ModalDevice: function () {
      var modal = this;
      var title = "Add device to facility"
      var form = this.form = new twentyc.rest.Form(
        $ctl.template("form_assign_device")
      );

      this.select_device = new twentyc.rest.Select(this.form.element.find('#device'));

      this.select_device.load();

      $(this.form).on("api-write:success", (ev, e, payload, response) => {
        $ctl.devicectl.$t.devices.$w.list.load();
        $ctl.devicectl.$c.toolbar.$w.select_device.load();
        modal.hide();
      });

      this.form.format_request_url = (url) => {
        return url.replace(/facility_tag/, $ctl.devicectl.facility_slug());
      };

      this.Modal("save", title, form.element);
      form.wire_submit(this.$e.button_submit);
    }
  },
  $ctl.application.Modal
);



$ctl.application.Devicectl.ModalDevice = $tc.extend(
  "ModalDevice",
  {
    ModalDevice: function (device) {
      var modal = this;
      var title = "Add Device"
      var form = this.form = new twentyc.rest.Form(
        $ctl.template("form_device")
      );

      $.ajax(
        {
          method: "options",
          url: form.base_url
        }
      ).done((data) => {

        var type_select = form.element.find('[name="type"]');
        /*
          * used to load device types (currently free form)
        var options = data.data[0].actions.POST.type.choices;

        $(options).each(function() {
          type_select.append(
            $('<option>').val(this.value).text(this.display_name)
          )
        });
        */

        if (device)
          type_select.val(device.type);

      });

      this.device = device;

      form.fill({ facility: fullctl.devicectl.facility() })

      if (device) {
        title = "Edit " + device.display_name;
        form.method = "PUT"
        form.form_action = device.id;
        form.fill(device);


        form.element.find('input[type="text"],select,input[type="checkbox"]').each(function () {
          if (!grainy.check(device.grainy + "." + $(this).attr("name"), "u")) {
            $(this).attr("disabled", true)
          }
        });


        $(this.form).on("api-write:before", (ev, e, payload) => {
          payload["id"] = device.id;
        });
      }

      $(this.form).on("api-write:success", (ev, e, payload, response) => {
        $ctl.devicectl.$t.devices.$w.list.load();
        modal.hide();
      });


      this.Modal("save_right", title, form.element);
      form.wire_submit(this.$e.button_submit);
    }
  },
  $ctl.application.Modal
);



// LOGICAL PORTS

$ctl.application.Devicectl.LogicalPorts = $tc.extend(
  "LogicalPorts",
  {
    LogicalPorts: function () {
      this.Tool("logical_ports");
    },
    init: function () {
      // v2 - create delete selected button
      this.delete_selected_button = this.$t.button_delete_selected;
      // v2 - create SelectionList
      this.widget("list", ($e) => {
        return new $ctl.widget.SelectionList(
          this.template("list", this.$e.body),
          $(this.delete_selected_button)
        );
      })

      this.$w.list.format_request_url = (url) => {
        return url.replace("/0/", "/" + fullctl.devicectl.device_id() + "/");
      };


      this.$w.list.formatters.row = (row, data) => {
        row.find('a[data-action="edit_logical_port"]').click(() => {
          var logical_port = row.data("apiobject");
          new $ctl.application.Devicectl.ModalLogicalPort(logical_port);
        }).each(function () {
          if (!grainy.check(data.grainy + ".?", "u")) {
            $(this).hide()
          }
        });

        var button_delete = new twentyc.rest.Button(
          row.find('a[data-element="delete_logical_port"]')
        );

        button_delete.format_request_url = (url) => {
          return url.replace("/0/", "/" + data.id + "/");
        };

        $(button_delete).on("api-write:success", () => $ctl.devicectl.sync());

        if (!grainy.check(data.grainy, "d")) {
          button_delete.element.hide();
        }


      };

      this.initialize_sortable_headers("name");

      $(this.$w.list).on("api_callback_remove:after", () => {
        $ctl.devicectl.sync();
      });
    },

    menu: function () {
      var menu = this.Tool_menu();
      menu.find('[data-element="button_add_logical_port"]').click(() => {
        return new $ctl.application.Devicectl.ModalLogicalPort();
      });

      // v2 - add/set-up delete selected button
      $(this.delete_selected_button).insertBefore(menu.find('[data-element="button_add_logical_port"]'));

      $(this.delete_selected_button).click(() => {
        if (confirm("Remove selected Logical Ports?")) {
          this.$w.list.delete_selected_list();
        }
      });

      return menu;
    },

    sync: function () {
      let namespace = `logical_port.${$ctl.org.id}`

      if (!fullctl.devicectl || !fullctl.devicectl.device_id()) {
        return;
      }

      if (grainy.check(namespace, "r")) {
        this.show();
        this.apply_ordering();
        this.$w.list.load();

        // v2 - set up view API button
        this.$e.bottom_menu.find('[data-element="button_api_view"]').attr(
          "href", this.$w.list.base_url.replace('/0/', "/" + fullctl.devicectl.device_id() + "/") + "/" + this.$w.list.action + "?pretty"
        )

        this.$e.menu.find('[data-element="button_add_logical_port"]').grainy_toggle(namespace, "c")

      } else {
        this.hide();
      }
    }
  },
  $ctl.application.Tool
);

$ctl.application.Devicectl.ModalLogicalPort = $tc.extend(
  "ModalLogicalPort",
  {
    ModalLogicalPort: function (logical_port) {
      var modal = this;
      var title = "Add LogicalPort"
      var form = this.form = new twentyc.rest.Form(
        $ctl.template("form_logical_port")
      );

      this.logical_port = logical_port;

      if (logical_port) {
        title = "Edit " + logical_port.display_name;
        form.method = "PUT"
        form.form_action = logical_port.id;
        form.fill(logical_port);


        form.element.find('input[type="text"],select,input[type="checkbox"]').each(function () {
          if (!grainy.check(logical_port.grainy + "." + $(this).attr("name"), "u")) {
            $(this).attr("disabled", true)
          }
        });


        $(this.form).on("api-write:before", (ev, e, payload) => {
          payload["id"] = logical_port.id;
        });
      }

      $(this.form).on("api-write:success", (ev, e, payload, response) => {
        $ctl.devicectl.$t.logical_ports.$w.list.load();
        $ctl.devicectl.$t.physical_ports.$w.list.load();
        modal.hide();
      });

      this.Modal("save_right", title, form.element);
      form.wire_submit(this.$e.button_submit);
    }
  },
  $ctl.application.Modal
);

// PHYSICAL PORTS

$ctl.application.Devicectl.PhysicalPorts = $tc.extend(
  "PhysicalPorts",
  {
    PhysicalPorts: function () {
      this.Tool("physical_ports");
    },
    init: function () {
      // v2 - create delete selected button
      this.delete_selected_button = this.$t.button_delete_selected;
      // v2 - create SelectionList
      this.widget("list", ($e) => {
        return new $ctl.widget.SelectionList(
          this.template("list", this.$e.body),
          $(this.delete_selected_button)
        );
      })

      this.$w.list.formatters.row = (row, data) => {
        row.find('a[data-action="edit_physical_port"]').click(() => {
          var physical_port = row.data("apiobject");
          new $ctl.application.Devicectl.ModalPhysicalPort(physical_port);
        }).each(function () {
          if (!grainy.check(data.grainy + ".?", "u")) {
            $(this).hide()
          }
        });

        var button_delete = new twentyc.rest.Button(
          row.find('a[data-element="delete_physical_port"]')
        );

        button_delete.format_request_url = (url) => {
          return url.replace("/0/", "/" + data.id + "/");
        };

        $(button_delete).on("api-write:success", () => $ctl.devicectl.sync());

        if (!grainy.check(data.grainy, "d")) {
          button_delete.element.hide();
        }
      };

      this.$w.list.format_request_url = (url) => {
        return url.replace("/0/", "/" + fullctl.devicectl.device_id() + "/");
      };

      $(this.$w.list).on("api-delete:after", () => {
        $ctl.devicectl.sync();
      });

      this.initialize_sortable_headers("name");
    },

    menu: function () {
      var menu = this.Tool_menu();
      menu.find('[data-element="button_add_physical_port"]').click(() => {
        return new $ctl.application.Devicectl.ModalPhysicalPort();
      });

      $(this.delete_selected_button).insertBefore(menu.find('[data-element="button_add_physical_port"]'));
      $(this.delete_selected_button).click(() => {
        if (confirm("Remove selected Physical Ports?")) {
          this.$w.list.delete_selected_list();
        }
      });

      return menu;
    },

    sync: function () {
      if (!fullctl.devicectl || !fullctl.devicectl.device_id()) {
        return;
      }


      let namespace = `physical_port.${$ctl.org.id}`
      if (grainy.check(namespace, "r")) {
        this.show();
        this.apply_ordering();
        this.$w.list.load();

        // v2 - set up view API button
        this.$e.bottom_menu.find('[data-element="button_api_view"]').attr(
          "href", this.$w.list.base_url.replace('/0/', "/" + fullctl.devicectl.device_id() + "/") + "/" + this.$w.list.action + "?pretty"
        )

        this.$e.menu.find('[data-element="button_add_physical_port"]').grainy_toggle(namespace, "c")

      } else {
        this.hide();
      }
    }
  },
  $ctl.application.Tool
);

$ctl.application.Devicectl.ModalPhysicalPort = $tc.extend(
  "ModalPhysicalPort",
  {
    ModalPhysicalPort: function (physical_port) {
      var modal = this;
      var title = "Add PhysicalPort"
      var form = this.form = new twentyc.rest.Form(
        $ctl.template("form_physical_port")
      );

      var logical_port_select = this.logical_port_select = new twentyc.rest.Select(
        form.element.find('select[name="logical_port"]')
      )

      logical_port_select.format_request_url = (url) => {
        return url.replace("/fac_tag/", "/" + fullctl.devicectl.facility_slug() + "/");
      };

      logical_port_select.load().then(() => {
        if (physical_port) { logical_port_select.element.val(physical_port.logical_port) }
      });
      this.physical_port = physical_port;

      if (physical_port) {
        title = "Edit " + physical_port.display_name;
        form.method = "PUT"
        form.form_action = physical_port.id;
        form.fill(physical_port);


        form.element.find('input[type="text"],select,input[type="checkbox"]').each(function () {
          if (!grainy.check(physical_port.grainy + "." + $(this).attr("name"), "u")) {
            $(this).attr("disabled", true)
          }
        });


        $(this.form).on("api-write:before", (ev, e, payload) => {
          payload["id"] = physical_port.id;
        });
      }

      form.fill({
        device: fullctl.devicectl.device_id(),
        device_name: fullctl.devicectl.device_name(),
      })

      $(this.form).on("api-write:success", (ev, e, payload, response) => {
        $ctl.devicectl.$t.physical_ports.$w.list.load();
        $ctl.devicectl.$t.logical_ports.$w.list.load();
        modal.hide();
      });

      this.Modal("save_right", title, form.element);
      form.wire_submit(this.$e.button_submit);
    }
  },
  $ctl.application.Modal
);


// VIRTUAL PORTS

$ctl.application.Devicectl.VirtualPorts = $tc.extend(
  "VirtualPorts",
  {
    VirtualPorts: function () {
      this.Tool("virtual_ports");
    },
    init: function () {
      // v2 - create delete selected button
      this.delete_selected_button = this.$t.button_delete_selected;
      // v2 - create SelectionList
      this.widget("list", ($e) => {
        return new $ctl.widget.SelectionList(
          this.template("list", this.$e.body),
          $(this.delete_selected_button)
        );
      })

      this.$w.list.formatters.row = (row, data) => {
        row.find('a[data-action="edit_virtual_port"]').click(() => {
          var virtual_port = row.data("apiobject");
          new $ctl.application.Devicectl.ModalVirtualPort(virtual_port);
        }).each(function () {
          if (!grainy.check(data.grainy + ".?", "u")) {
            $(this).hide()
          }
        });

        var button_delete = new twentyc.rest.Button(
          row.find('a[data-element="delete_virtual_port"]')
        );

        button_delete.format_request_url = (url) => {
          return url.replace("/0/", "/" + data.id + "/");
        };

        $(button_delete).on("api-write:success", () => $ctl.devicectl.sync());

        if (!grainy.check(data.grainy, "d")) {
          button_delete.element.hide();
        }
      };

      this.$w.list.format_request_url = (url) => {
        return url.replace("/0/", "/" + fullctl.devicectl.device_id() + "/");
      };

      this.initialize_sortable_headers("name");
    },

    menu: function () {
      let menu = this.Tool_menu();
      menu.find('[data-element="button_add_virtual_port"]').click(() => {
        return new $ctl.application.Devicectl.ModalVirtualPort();
      });

      // v2 - add/setup delete selected button
      $(this.delete_selected_button).insertBefore(menu.find('[data-element="button_add_virtual_port"]'));
      $(this.delete_selected_button).click(() => {
        if (confirm("Remove selected Virtual Ports?")) {
          this.$w.list.delete_selected_list();
        }
      });

      return menu;
    },

    sync: function () {
      let namespace = `virtual_port.${$ctl.org.id}`

      if (!fullctl.devicectl || !fullctl.devicectl.device_id()) {
        return;
      }

      if (grainy.check(namespace, "r")) {
        this.show();
        this.apply_ordering();
        this.$w.list.load();

        // v2 - set up view API button
        this.$e.bottom_menu.find('[data-element="button_api_view"]').attr(
          "href", this.$w.list.base_url.replace('/0/', "/" + fullctl.devicectl.device_id() + "/") + "/" + this.$w.list.action + "?pretty"
        )

        this.$e.menu.find('[data-element="button_add_virtual_port"]').grainy_toggle(namespace, "c")

      } else {
        this.hide();
      }
    }
  },
  $ctl.application.Tool
);

$ctl.application.Devicectl.ModalVirtualPort = $tc.extend(
  "ModalVirtualPort",
  {
    ModalVirtualPort: function (virtual_port) {
      var modal = this;
      var title = "Add VirtualPort"
      var form = this.form = new twentyc.rest.Form(
        $ctl.template("form_virtual_port")
      );

      var logical_port_select = this.logical_port_select = new twentyc.rest.Select(
        form.element.find('select[name="logical_port"]')
      )

      logical_port_select.format_request_url = (url) => {
        return url.replace("/0/", "/" + fullctl.devicectl.device_id() + "/");
      };

      logical_port_select.load().then(() => {
        if (virtual_port) { logical_port_select.element.val(virtual_port.logical_port) }
      });
      this.virtual_port = virtual_port;

      if (virtual_port) {
        title = "Edit " + virtual_port.display_name;
        form.method = "PUT"
        form.form_action = virtual_port.id;
        form.fill(virtual_port);


        form.element.find('input[type="text"],select,input[type="checkbox"]').each(function () {
          if (!grainy.check(virtual_port.grainy + "." + $(this).attr("name"), "u")) {
            $(this).attr("disabled", true)
          }
        });


        $(this.form).on("api-write:before", (ev, e, payload) => {
          payload["id"] = virtual_port.id;
        });
      }

      $(this.form).on("api-write:success", (ev, e, payload, response) => {
        $ctl.devicectl.$t.virtual_ports.$w.list.load();
        modal.hide();
      });

      this.Modal("save_right", title, form.element);
      form.wire_submit(this.$e.button_submit);
    }
  },
  $ctl.application.Modal
);



$(document).ready(function () {
  $ctl.devicectl = new $ctl.application.Devicectl();
});

})(jQuery, twentyc.cls, fullctl);