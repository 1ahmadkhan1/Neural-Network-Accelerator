
module basics (
	clk_clk,
	leds_export,
	reset_reset_n,
	sev_seg_export,
	switches_export);	

	input		clk_clk;
	output	[9:0]	leds_export;
	input		reset_reset_n;
	output	[6:0]	sev_seg_export;
	input	[9:0]	switches_export;
endmodule
