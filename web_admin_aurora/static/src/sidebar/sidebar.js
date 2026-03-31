/** @odoo-module **/

import { Component, useState, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class SideBar extends Component {
    setup() {
        this.menuService = useService("menu");
        this.actionService = useService("action");
        this.orm = useService("orm");
        this.state = useState({
            isCollapsed: false,
            expandedMenuIds: {},
            branding: {
                logo: "",
                title: "Odoo",
            }
        });

        this.loadBranding();


        const update = () => {
            this.autoExpandActive();
            this.render();
        };
        const onToggleSidebar = () => this.toggleSidebar();
        this.env.bus.addEventListener("MENUS:APP-CHANGED", update);
        this.env.bus.addEventListener("AURORA:TOGGLE-SIDEBAR", onToggleSidebar);
        onWillUnmount(() => {
            this.env.bus.removeEventListener("MENUS:APP-CHANGED", update);
            this.env.bus.removeEventListener("AURORA:TOGGLE-SIDEBAR", onToggleSidebar);
        });

        this.autoExpandActive();
    }

    async loadBranding() {
        try {
            const config = await this.orm.call("res.company", "get_branding_config", []);
            this.state.branding.title = config.title || "ADSMO";
            if (config.favicon) {
                this.state.branding.logo = `data:image/x-icon;base64,${config.favicon}`;
            }
        } catch (e) {
            console.error("Failed to load branding", e);
        }
    }




    autoExpandActive() {
        const currentApp = this.menuService.getCurrentApp();
        if (currentApp) {
            const tree = this.menuService.getMenuAsTree(currentApp.id);
            const expandSelected = (node) => {
                if (node.isSelected) {
                    this.state.expandedMenuIds[node.id] = true;
                    return true;
                }
                let childSelected = false;
                for (const child of node.childrenTree) {
                    if (expandSelected(child)) {
                        childSelected = true;
                    }
                }
                if (childSelected) {
                    this.state.expandedMenuIds[node.id] = true;
                }
                return childSelected;
            };
            expandSelected(tree);
        }
    }



    get apps() {
        return this.menuService.getApps();
    }

    get currentApp() {
        return this.menuService.getCurrentApp();
    }

    get currentAppSections() {
        return (
            (this.currentApp && this.menuService.getMenuAsTree(this.currentApp.id).childrenTree) ||
            []
        );
    }

    getIconSrc(app) {
        let src = app.webIconData;
        if (!src && app.webIcon) {
            const [module, path] = app.webIcon.split(",");
            src = `/${module}/${path}`;
        }
        if (!src) return "";
        if (src.startsWith("data:") || src.startsWith("/") || src.startsWith("http")) {
            return src;
        }
        return `data:image/png;base64,${src}`;
    }




    toggleSidebar() {
        this.state.isCollapsed = !this.state.isCollapsed;
        document.body.classList.toggle("o_sidebar_collapsed", this.state.isCollapsed);
        
        // For mobile
        if (window.innerWidth < 768) {
            const sidebar = document.querySelector(".o_aurora_sidebar");
            if (sidebar) {
                sidebar.classList.toggle("o_mobile_show");
            }
        }
    }


    onMenuClick(menu) {
        if (menu.childrenTree && menu.childrenTree.length > 0) {
            this.state.expandedMenuIds[menu.id] = !this.state.expandedMenuIds[menu.id];
        }
        if (menu.actionID) {
            this.menuService.selectMenu(menu);
        }
    }

    isMenuExpanded(menu) {
        return !!this.state.expandedMenuIds[menu.id] || this.isMenuSelected(menu);
    }



    isMenuSelected(menu) {
        const currentApp = this.menuService.getCurrentApp();
        if (!currentApp) return false;
        const tree = this.menuService.getMenuAsTree(currentApp.id);
        
        // Check if this menu or any of its children are selected
        const findInTree = (node) => {
            if (node.id === menu.id) return node.isSelected;
            for (const child of node.childrenTree) {
                if (findInTree(child)) return true;
            }
            return false;
        };
        return findInTree(tree);
    }

    getMenuItemHref(menu) {
        const parts = [`menu_id=${menu.id}`];
        if (menu.actionID) {
            parts.push(`action_id=${menu.actionID}`);
        }
        return `#${parts.join("&")}`;
    }
}



SideBar.template = "web_admin_aurora.SideBar";
SideBar.components = {};
