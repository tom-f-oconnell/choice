// Generated with make_3d.py from master DXF, ../olfactory_shock_conditioning_chambers.dxf
// Uses ezdxf and solidpython
// It seems solidpython needs to be updated to use import and linear extrude, 
// rather than dxf_linear_extrude.


color(c = [1, 1, 1, 0.2000000000]) {
	dxf_linear_extrude(file = "../olfactory_shock_conditioning_chambers.dxf", height = 3.1750000000, layer = "9_trap_bottomplate");
}

color(c = [1, 1, 1, 0.2000000000]) {
	translate(v = [0, 0, 3.1750000000]) {
		dxf_linear_extrude(file = "../olfactory_shock_conditioning_chambers.dxf", height = 3.1750000000, layer = "8_flow_regulator_retainers");
	}
}

color(c = [1, 1, 1, 0.2000000000]) {
	translate(v = [0, 0, 6.3500000000]) {
		dxf_linear_extrude(file = "../olfactory_shock_conditioning_chambers.dxf", height = 3.1750000000, layer = "7_vacuum_trap_sliders");
	}
}

color(c = [1, 1, 1, 0.2000000000]) {
	translate(v = [0, 0, 9.5250000000]) {
		dxf_linear_extrude(file = "../olfactory_shock_conditioning_chambers.dxf", height = 3.1750000000, layer = "6.1_vacuum_trap_guides");
	}
}

color(c = [1, 1, 1, 0.2000000000]) {
	translate(v = [0, 0, 12.7000000000]) {
		dxf_linear_extrude(file = "../olfactory_shock_conditioning_chambers.dxf", height = 3.1750000000, layer = "5_support_acrylic");
	}
}

color(c = [0.1568627451, 0.9372549020, 0.7019607843, 0.9000000000]) {
	translate(v = [0, 0, 15.8750000000]) {
		dxf_linear_extrude(file = "../olfactory_shock_conditioning_chambers.dxf", height = 1.5875000000, layer = "4.2_bottom_pcb_edges_and_routing");
	}
}

color(c = [0, 0, 0, 1]) {
	translate(v = [0, 0, 15.8750000000]) {
		dxf_linear_extrude(file = "../olfactory_shock_conditioning_chambers.dxf", height = 1.5875000000, layer = "4.1_pcb_side_spacers");
	}
}

color(c = [1, 1, 0, 0.9500000000]) {
	translate(v = [0, 0, 17.4625000000]) {
		dxf_linear_extrude(file = "../olfactory_shock_conditioning_chambers.dxf", height = 0.3969000000, layer = "3.1_yellow_manifold_layer");
	}
}

color(c = [1, 1, 1, 0.2000000000]) {
	translate(v = [0, 0, 17.8594000000]) {
		dxf_linear_extrude(file = "../olfactory_shock_conditioning_chambers.dxf", height = 3.1750000000, layer = "2.2_delrin_sliders");
	}
}

color(c = [1, 1, 1, 0.9000000000]) {
	translate(v = [0, 0, 17.8594000000]) {
		dxf_linear_extrude(file = "../olfactory_shock_conditioning_chambers.dxf", height = 0.7938000000, layer = "2.1_delrin_chambers_and_manifold");
	}
}

color(c = [1, 1, 1, 0.2000000000]) {
	translate(v = [0, 0, 18.6532000000]) {
		dxf_linear_extrude(file = "../olfactory_shock_conditioning_chambers.dxf", height = 3.1750000000, layer = "1.3_servo_arm_spacer");
	}
}

color(c = [1, 1, 1, 0.2000000000]) {
	translate(v = [0, 0, 18.6532000000]) {
		dxf_linear_extrude(file = "../olfactory_shock_conditioning_chambers.dxf", height = 3.1750000000, layer = "1.2a_top_pcb_edges_and_routing");
	}
}

color(c = [1, 1, 1, 0.2000000000]) {
	translate(v = [0, 0, 18.6532000000]) {
		dxf_linear_extrude(file = "../olfactory_shock_conditioning_chambers.dxf", height = 3.1750000000, layer = "1.1_top_acrylic_manifold_sides");
	}
}

color(c = [1, 1, 1, 0.2000000000]) {
	translate(v = [0, 0, 21.8282000000]) {
		dxf_linear_extrude(file = "../olfactory_shock_conditioning_chambers.dxf", height = 3.1750000000, layer = "0_servo_arm");
	}
}

color(c = [1, 1, 1, 0.9000000000]) {
	translate(v = [0, 0, 21.8282000000]) {
		dxf_linear_extrude(file = "../olfactory_shock_conditioning_chambers.dxf", height = 1.5875000000, layer = "0.2a_slider_compression");
	}
}