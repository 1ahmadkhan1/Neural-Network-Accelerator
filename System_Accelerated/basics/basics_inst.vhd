	component basics is
		port (
			clk_clk         : in  std_logic                    := 'X';             -- clk
			leds_export     : out std_logic_vector(9 downto 0);                    -- export
			reset_reset_n   : in  std_logic                    := 'X';             -- reset_n
			sev_seg_export  : out std_logic_vector(6 downto 0);                    -- export
			switches_export : in  std_logic_vector(9 downto 0) := (others => 'X')  -- export
		);
	end component basics;

	u0 : component basics
		port map (
			clk_clk         => CONNECTED_TO_clk_clk,         --      clk.clk
			leds_export     => CONNECTED_TO_leds_export,     --     leds.export
			reset_reset_n   => CONNECTED_TO_reset_reset_n,   --    reset.reset_n
			sev_seg_export  => CONNECTED_TO_sev_seg_export,  --  sev_seg.export
			switches_export => CONNECTED_TO_switches_export  -- switches.export
		);

