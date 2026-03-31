/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";
import { Component, onWillStart, onMounted, useState, useEffect, useEnv } from "@odoo/owl";

const today = new Date();
const formattedDate = `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`;

export class RoomChart extends Component {
    static template = "hotel_management_odoo.RoomChart";
    static props = false;

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.user = useService("user");
        this.env = useEnv();

        // isAdmin must be in useState so Owl tracks it reactively
        this.state = useState({
            rooms: [],
            counts: {},
            floors: [],
            room_types: [],
            currentFilter: "all",
            currentRoomType: "all",
            targetDate: "",
            dash: {},
            isAdmin: false,
        });

        this.allRooms = [];
        this.revenue_chart = null;
        this.occupancy_chart = null;
        this.chartLoaded = false;
        this.dashRevision = 0;
        this.lastDashRevision = -1;
        this.trend_labels = [];
        this.revenue_trend = [];
        this.occupancy_trend = [];

        onWillStart(async () => {
            try {
                const isAdmin = await this.user.hasGroup("hotel_management_odoo.hotel_group_admin");
                this.state.isAdmin = isAdmin;
            } catch (e) {
                console.warn("Failed to check admin group:", e);
            }
            try {
                await this.fetchData();
            } catch (e) {
                console.error("Failed to load room chart data:", e);
            }
            try {
                await this.fetchDashboardData();
            } catch (e) {
                console.error("Failed to load dashboard data:", e);
            }
        });

        onMounted(() => {
            // Load Chart.js
            loadJS("/web/static/lib/Chart/Chart.js").then(() => {
                this.chartLoaded = true;
                this.render_graphs();
            }).catch((e) => {
                console.warn("Failed to load Chart.js:", e);
            });

            // Subscribe to Odoo Bus for real-time room status updates
            // Access bus_service safely via env.services to avoid crashing setup()
            try {
                const busService = this.env.services["bus_service"];
                if (busService) {
                    busService.addChannel("hotel_room_status_channel").then(() => {
                        busService.subscribe("hotel_room_status_changed", (payload) => {
                            console.log("Room status changed, refreshing Room Chart...", payload);
                            this.refreshData();
                        });
                    }).catch((e) => {
                        console.warn("Bus service addChannel failed:", e);
                    });
                }
            } catch (e) {
                console.warn("Bus service not available:", e);
            }
        });

        useEffect(() => {
            if (this.chartLoaded && this.state.dash && this.dashRevision !== this.lastDashRevision) {
                this.lastDashRevision = this.dashRevision;
                this.render_graphs();
            }
        });
    }

    async fetchData() {
        const data = await this.orm.call("room.booking", "get_room_chart_data", [], {
            loaiphong_id: this.state.currentRoomType,
            target_date: this.state.targetDate || null,
        });
        this.allRooms = data.rooms;
        this.state.counts = data.counts;
        this.state.floors = data.floors;
        this.state.room_types = data.room_types;
        this.filterRoomsLocal();
    }

    filterRoomsLocal() {
        if (this.state.currentFilter === "all") {
            this.state.rooms = [...this.allRooms];
        } else {
            this.state.rooms = this.allRooms.filter((room) => {
                if (this.state.currentFilter === "arriving") return room.booking_state === "reserved";
                if (this.state.currentFilter === "in_house") return room.booking_state === "check_in";
                if (this.state.currentFilter === "departing") return room.is_departing === true;
                if (this.state.currentFilter === "available") return ["available", "clean"].includes(room.status);
                return room.status === this.state.currentFilter;
            });
        }
    }

    async onFilterStatus(status) {
        this.state.currentFilter = status;
        this.filterRoomsLocal();
    }

    async onRoomTypeChange(ev) {
        this.state.currentRoomType = ev.target.value;
        await this.fetchData();
        this.fetchDashboardData();
    }

    async onDateChange(ev) {
        this.state.targetDate = ev.target.value;
        await this.fetchData();
        this.fetchDashboardData();
    }

    async refreshData() {
        await this.fetchData();
        await this.fetchDashboardData();
    }

    get groupedRooms() {
        const grouped = {};
        this.state.floors.forEach((floor) => {
            grouped[floor.id] = { floor: floor, rooms: [] };
        });
        grouped[0] = { floor: { id: 0, name: "Khác" }, rooms: [] };
        this.state.rooms.forEach((room) => {
            const floorId = room.floor_id || 0;
            if (!grouped[floorId]) {
                grouped[floorId] = { floor: { id: floorId, name: room.floor_name }, rooms: [] };
            }
            grouped[floorId].rooms.push(room);
        });
        const sortedGroups = this.state.floors
            .map((floor) => grouped[floor.id])
            .filter((g) => g.rooms.length > 0)
            .concat(grouped[0].rooms.length > 0 ? [grouped[0]] : []);
        return sortedGroups;
    }

    openRoom(room) {
        if (room.booking_id) {
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "room.booking",
                res_id: room.booking_id,
                views: [[false, "form"]],
                target: "current",
            });
        } else {
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "hotel.room",
                res_id: room.id,
                views: [[false, "form"]],
                target: "current",
            });
        }
    }

    async fetchDashboardData() {
        const result = await this.orm.call("room.booking", "get_details", [{}], {});
        if (result["currency_position"] === "before") {
            result["total_revenue"] = result["currency_symbol"] + " " + result["total_revenue"];
            result["today_revenue"] = result["currency_symbol"] + " " + result["today_revenue"];
            result["pending_payment"] = result["currency_symbol"] + " " + result["pending_payment"];
            result["adr"] = result["currency_symbol"] + " " + result["adr"];
            result["revpar"] = result["currency_symbol"] + " " + result["revpar"];
        } else {
            result["total_revenue"] = result["total_revenue"] + " " + result["currency_symbol"];
            result["today_revenue"] = result["today_revenue"] + " " + result["currency_symbol"];
            result["pending_payment"] = result["pending_payment"] + " " + result["currency_symbol"];
            result["adr"] = result["adr"] + " " + result["currency_symbol"];
            result["revpar"] = result["revpar"] + " " + result["currency_symbol"];
        }
        this.state.dash = result;
        this.trend_labels = result["trend_labels"];
        this.revenue_trend = result["revenue_trend"];
        this.occupancy_trend = result["occupancy_trend"];
        this.dashRevision++;
    }

    render_graphs() {
        this.render_revenue_chart();
        this.render_occupancy_chart();
    }

    render_revenue_chart() {
        const ctx = document.getElementById("revenue_trend_chart");
        if (!ctx) return;
        if (this.revenue_chart) {
            this.revenue_chart.data.labels = this.trend_labels;
            this.revenue_chart.data.datasets[0].data = this.revenue_trend;
            this.revenue_chart.update();
        } else {
            this.revenue_chart = new Chart(ctx, {
                type: "line",
                data: {
                    labels: this.trend_labels,
                    datasets: [{
                        label: "Revenue",
                        data: this.revenue_trend,
                        borderColor: "#9c27b0",
                        backgroundColor: "rgba(156, 39, 176, 0.1)",
                        fill: true,
                        tension: 0.4,
                    }],
                },
                options: { responsive: true, maintainAspectRatio: false },
            });
        }
    }

    render_occupancy_chart() {
        const ctx = document.getElementById("occupancy_trend_chart");
        if (!ctx) return;
        if (this.occupancy_chart) {
            this.occupancy_chart.data.labels = this.trend_labels;
            this.occupancy_chart.data.datasets[0].data = this.occupancy_trend;
            this.occupancy_chart.update();
        } else {
            this.occupancy_chart = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: this.trend_labels,
                    datasets: [{
                        label: "Occupied Rooms",
                        data: this.occupancy_trend,
                        backgroundColor: "#00bcd4",
                    }],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
                },
            });
        }
    }

    total_rooms(e) {
        e.preventDefault();
        this.action.doAction({ name: _t("Rooms"), type: "ir.actions.act_window", res_model: "hotel.room", view_mode: "tree,form", views: [[false, "list"], [false, "form"]], target: "current" });
    }

    check_ins(e) {
        e.preventDefault();
        this.action.doAction({ name: _t("Check-In"), type: "ir.actions.act_window", res_model: "room.booking", view_mode: "tree,form", views: [[false, "list"], [false, "form"]], domain: [["state", "=", "check_in"]], target: "current" });
    }

    view_total_events(e) {
        e.preventDefault();
        this.action.doAction({ name: _t("Total Events"), type: "ir.actions.act_window", res_model: "event.event", view_mode: "kanban,tree,form", views: [[false, "kanban"], [false, "list"], [false, "form"]], target: "current" });
    }

    fetch_today_events(e) {
        e.preventDefault();
        this.action.doAction({ name: _t("Today's Events"), type: "ir.actions.act_window", res_model: "event.event", view_mode: "kanban,tree,form", views: [[false, "kanban"], [false, "list"], [false, "form"]], domain: [["date_end", "=", formattedDate]], target: "current" });
    }

    fetch_pending_events(e) {
        e.preventDefault();
        this.action.doAction({ name: _t("Pending Events"), type: "ir.actions.act_window", res_model: "event.event", view_mode: "kanban,tree,form", views: [[false, "kanban"], [false, "list"], [false, "form"]], domain: [["date_end", ">=", formattedDate]], target: "current" });
    }

    fetch_total_staff(e) {
        e.preventDefault();
        this.action.doAction({ name: _t("Total Staffs"), type: "ir.actions.act_window", res_model: "res.users", view_mode: "tree,form", views: [[false, "list"], [false, "form"]], domain: [["groups_id.name", "in", ["Admin", "Cleaning Team User", "Cleaning Team Head", "Receptionist", "Maintenance Team User", "Maintenance Team Leader"]]], target: "current" });
    }

    check_outs(e) {
        if (e) e.preventDefault();
        const start = `${formattedDate} 00:00:00`;
        const end = `${formattedDate} 23:59:59`;
        this.action.doAction({ name: _t("Today's Check-Out"), type: "ir.actions.act_window", res_model: "room.booking", view_mode: "tree,form", views: [[false, "list"], [false, "form"]], domain: [["room_line_ids.checkout_date", ">=", start], ["room_line_ids.checkout_date", "<=", end]], target: "current" });
    }

    available_rooms(e) {
        e.preventDefault();
        this.action.doAction({ name: _t("Available Room"), type: "ir.actions.act_window", res_model: "hotel.room", view_mode: "tree,form", views: [[false, "list"], [false, "form"]], domain: [["status", "in", ["available", "clean"]]], target: "current" });
    }

    reservations(e) {
        e.preventDefault();
        this.action.doAction({ name: _t("Total Reservations"), type: "ir.actions.act_window", res_model: "room.booking", view_mode: "tree,form", views: [[false, "list"], [false, "form"]], domain: [["state", "=", "reserved"]], target: "current" });
    }

    fetch_food_item(e) {
        e.preventDefault();
        this.action.doAction({ name: _t("Food Items"), type: "ir.actions.act_window", res_model: "lunch.product", view_mode: "tree,form", views: [[false, "list"], [false, "form"]], target: "current" });
    }

    async fetch_food_order(e) {
        e.preventDefault();
        const result = await this.orm.call("food.booking.line", "search_food_orders", [{}], {});
        this.action.doAction({ name: _t("Food Orders"), type: "ir.actions.act_window", res_model: "food.booking.line", view_mode: "tree,form", views: [[false, "list"], [false, "form"]], domain: [["id", "in", result]], target: "current" });
    }

    fetch_total_vehicle(e) {
        e.preventDefault();
        this.action.doAction({ name: _t("Total Vehicles"), type: "ir.actions.act_window", res_model: "fleet.vehicle.model", view_mode: "tree,form", views: [[false, "list"], [false, "form"]], target: "current" });
    }

    async fetch_available_vehicle(e) {
        e.preventDefault();
        const result = await this.orm.call("fleet.booking.line", "search_available_vehicle", [{}], {});
        this.action.doAction({ name: _t("Available Vehicle"), type: "ir.actions.act_window", res_model: "fleet.vehicle.model", view_mode: "tree,form", views: [[false, "list"], [false, "form"]], domain: [["id", "not in", result]], target: "current" });
    }
}

registry.category("actions").add("hotel_room_chart", RoomChart);
