"""
Bitwig MCP Tools

This module provides MCP tools for controlling Bitwig Studio.
"""

import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List

from mcp.types import TextContent, Tool

from bitwig_mcp_server.osc.controller import BitwigOSCController
from bitwig_mcp_server.utils.device_recommender import BitwigDeviceRecommender

# Set up logging
logger = logging.getLogger(__name__)


def get_bitwig_tools() -> List[Tool]:
    """Get all available Bitwig tools

    Returns:
        List of Tool objects
    """
    return [
        # Browser content discovery tools
        Tool(
            name="search_device_browser",
            description="Search for devices in the Bitwig browser using semantic search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'delay with filtering')",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5,
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by device category",
                    },
                    "type": {
                        "type": "string",
                        "description": "Filter by device type",
                    },
                    "creator": {
                        "type": "string",
                        "description": "Filter by device creator",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="recommend_devices",
            description="Recommend devices based on a natural language description of the desired sound or effect",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Description of the desired sound or effect (e.g., 'make the bass sound fatter and warmer')",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5,
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by device category",
                    },
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="get_device_categories",
            description="Get a list of all device categories",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_device_info",
            description="Get detailed information about a specific device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Name of the device to get information about",
                    },
                },
                "required": ["device_name"],
            },
        ),
        Tool(
            name="transport_play",
            description="Toggle play/pause state of Bitwig",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="set_tempo",
            description="Set the tempo of the Bitwig project",
            inputSchema={
                "type": "object",
                "properties": {
                    "bpm": {
                        "type": "number",
                        "description": "Tempo in beats per minute (0-666)",
                    }
                },
                "required": ["bpm"],
            },
        ),
        Tool(
            name="set_track_volume",
            description="Set the volume of a track",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_index": {
                        "type": "integer",
                        "description": "Track index (1-based)",
                    },
                    "volume": {
                        "type": "number",
                        "description": "Volume value (0-128, where 64 is 0dB)",
                    },
                },
                "required": ["track_index", "volume"],
            },
        ),
        Tool(
            name="set_track_pan",
            description="Set the pan of a track",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_index": {
                        "type": "integer",
                        "description": "Track index (1-based)",
                    },
                    "pan": {
                        "type": "number",
                        "description": "Pan value (0-128, where 64 is center)",
                    },
                },
                "required": ["track_index", "pan"],
            },
        ),
        Tool(
            name="toggle_track_mute",
            description="Toggle mute state of a track",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_index": {
                        "type": "integer",
                        "description": "Track index (1-based)",
                    }
                },
                "required": ["track_index"],
            },
        ),
        Tool(
            name="set_device_parameter",
            description="Set value of a device parameter",
            inputSchema={
                "type": "object",
                "properties": {
                    "param_index": {
                        "type": "integer",
                        "description": "Parameter index (1-based)",
                    },
                    "value": {
                        "type": "number",
                        "description": "Parameter value (0-128)",
                    },
                },
                "required": ["param_index", "value"],
            },
        ),
        Tool(
            name="toggle_device_bypass",
            description="Toggle bypass state of the currently selected device",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="select_device_sibling",
            description="Select a sibling device (in the same chain as current device)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sibling_index": {
                        "type": "integer",
                        "description": "Index of the sibling device (1-8)",
                    },
                },
                "required": ["sibling_index"],
            },
        ),
        Tool(
            name="navigate_device",
            description="Navigate to next/previous device",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["next", "previous"],
                        "description": "Navigation direction",
                    },
                },
                "required": ["direction"],
            },
        ),
        Tool(
            name="enter_device_layer",
            description="Enter a device layer/chain",
            inputSchema={
                "type": "object",
                "properties": {
                    "layer_index": {
                        "type": "integer",
                        "description": "Index of the layer to enter (1-8)",
                    },
                },
                "required": ["layer_index"],
            },
        ),
        Tool(
            name="exit_device_layer",
            description="Exit current device layer (go to parent)",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="toggle_device_window",
            description="Toggle device window visibility",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        # Browser tools
        Tool(
            name="browse_insert_device",
            description="Open browser to insert a device after the selected device",
            inputSchema={
                "type": "object",
                "properties": {
                    "position": {
                        "type": "string",
                        "enum": ["after", "before"],
                        "description": "Position to insert device (before or after selected device)",
                        "default": "after",
                    },
                },
            },
        ),
        Tool(
            name="browse_device_presets",
            description="Open browser to browse presets for the selected device",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="commit_browser_selection",
            description="Commit the current selection in the browser",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="cancel_browser",
            description="Cancel the current browser session",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="navigate_browser_tab",
            description="Navigate to next or previous browser tab",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["next", "previous"],
                        "description": "Navigation direction",
                    },
                },
                "required": ["direction"],
            },
        ),
        Tool(
            name="navigate_browser_filter",
            description="Navigate through filter options in the browser",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_index": {
                        "type": "integer",
                        "description": "Index of the filter column (1-6)",
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["next", "previous"],
                        "description": "Navigation direction",
                    },
                },
                "required": ["filter_index", "direction"],
            },
        ),
        Tool(
            name="reset_browser_filter",
            description="Reset a browser filter column",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_index": {
                        "type": "integer",
                        "description": "Index of the filter column to reset (1-6)",
                    },
                },
                "required": ["filter_index"],
            },
        ),
        Tool(
            name="navigate_browser_result",
            description="Navigate through browser results",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["next", "previous"],
                        "description": "Navigation direction",
                    },
                },
                "required": ["direction"],
            },
        ),
        Tool(
            name="device_browser_workflow",
            description="Complete workflow for browsing and inserting a device",
            inputSchema={
                "type": "object",
                "properties": {
                    "position": {
                        "type": "string",
                        "enum": ["after", "before"],
                        "description": "Position to insert device (before or after selected device)",
                        "default": "after",
                    },
                    "num_tab_navigations": {
                        "type": "integer",
                        "description": "Number of tab navigations (+ for next, - for previous)",
                        "default": 0,
                    },
                    "filter_navigations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "filter_index": {
                                    "type": "integer",
                                    "description": "Index of the filter column (1-6)",
                                },
                                "steps": {
                                    "type": "integer",
                                    "description": "Number of navigation steps (+ for next, - for previous)",
                                },
                            },
                            "required": ["filter_index", "steps"],
                        },
                        "description": "List of filter navigation operations",
                    },
                    "result_navigations": {
                        "type": "integer",
                        "description": "Number of result navigations (+ for next, - for previous)",
                        "default": 0,
                    },
                },
            },
        ),
        Tool(
            name="preset_browser_workflow",
            description="Complete workflow for browsing and loading a preset",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_navigations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "filter_index": {
                                    "type": "integer",
                                    "description": "Index of the filter column (1-6)",
                                },
                                "steps": {
                                    "type": "integer",
                                    "description": "Number of navigation steps (+ for next, - for previous)",
                                },
                            },
                            "required": ["filter_index", "steps"],
                        },
                        "description": "List of filter navigation operations",
                    },
                    "result_navigations": {
                        "type": "integer",
                        "description": "Number of result navigations (+ for next, - for previous)",
                        "default": 0,
                    },
                },
            },
        ),
        Tool(
            name="add_track",
            description="Add a new track to the project (instrument, audio or effect)",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_type": {
                        "type": "string",
                        "enum": ["instrument", "audio", "effect"],
                        "description": "Kind of track to add",
                    }
                },
                "required": ["track_type"],
            },
        ),
        Tool(
            name="set_track_recarm",
            description="Arm or disarm a track for recording",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_index": {
                        "type": "integer",
                        "description": "Track index (1-based)",
                    },
                    "armed": {
                        "type": "boolean",
                        "description": "True to arm, False to disarm",
                    },
                },
                "required": ["track_index", "armed"],
            },
        ),
        Tool(
            name="create_clip",
            description="Create an empty clip in a clip slot",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_index": {
                        "type": "integer",
                        "description": "Track index (1-based)",
                    },
                    "slot_index": {
                        "type": "integer",
                        "description": "Clip slot index (1-8)",
                    },
                    "beats": {
                        "type": "integer",
                        "description": "Clip length in beats",
                    },
                },
                "required": ["track_index", "slot_index", "beats"],
            },
        ),
        Tool(
            name="launch_clip",
            description="Launch a clip in a clip slot",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_index": {
                        "type": "integer",
                        "description": "Track index (1-based)",
                    },
                    "slot_index": {
                        "type": "integer",
                        "description": "Clip slot index (1-8)",
                    },
                },
                "required": ["track_index", "slot_index"],
            },
        ),
        Tool(
            name="launch_scene",
            description="Launch a scene, starting every clip in that row",
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_index": {
                        "type": "integer",
                        "description": "Scene index (1-based)",
                    }
                },
                "required": ["scene_index"],
            },
        ),
        Tool(
            name="quantize_clip",
            description="Quantize the selected clip to Bitwig's grid setting",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="set_metronome",
            description="Turn the metronome click on or off",
            inputSchema={
                "type": "object",
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "description": "True for on, False for off",
                    }
                },
                "required": ["enabled"],
            },
        ),
        Tool(
            name="set_time_signature",
            description="Set the project time signature, for example 4/4",
            inputSchema={
                "type": "object",
                "properties": {
                    "signature": {
                        "type": "string",
                        "description": "Time signature as text, such as 4/4",
                    }
                },
                "required": ["signature"],
            },
        ),
        Tool(
            name="play_note",
            description=(
                "Play a single note live. Audible only if the track has an "
                "instrument, and captured only if a clip is recording"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "note": {
                        "type": "integer",
                        "description": "MIDI note number (0-127, 60 is middle C)",
                    },
                    "velocity": {
                        "type": "integer",
                        "description": "Velocity (0-127)",
                        "default": 100,
                    },
                    "duration_seconds": {
                        "type": "number",
                        "description": "How long to hold the note",
                        "default": 0.25,
                    },
                },
                "required": ["note"],
            },
        ),
        Tool(
            name="record_pattern",
            description=(
                "Record a note pattern into a clip. Creates the clip, arms the "
                "track, records while performing the notes in real time, then "
                "stops and quantizes. This is the only way to get notes into a "
                "clip, as OSC has no address for writing notes directly"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "track_index": {
                        "type": "integer",
                        "description": "Track index (1-based)",
                    },
                    "slot_index": {
                        "type": "integer",
                        "description": "Clip slot index (1-8)",
                    },
                    "length_beats": {
                        "type": "integer",
                        "description": "Clip length in beats",
                    },
                    "bpm": {
                        "type": "number",
                        "description": "Project tempo, used to time the performance",
                    },
                    "notes": {
                        "type": "array",
                        "description": "Notes to perform",
                        "items": {
                            "type": "object",
                            "properties": {
                                "note": {
                                    "type": "integer",
                                    "description": "MIDI note number (0-127)",
                                },
                                "start_beat": {
                                    "type": "number",
                                    "description": "Start position in beats from clip start",
                                },
                                "length_beats": {
                                    "type": "number",
                                    "description": "Note length in beats",
                                    "default": 0.5,
                                },
                                "velocity": {
                                    "type": "integer",
                                    "description": "Velocity (0-127)",
                                    "default": 100,
                                },
                            },
                            "required": ["note", "start_beat"],
                        },
                    },
                    "quantize": {
                        "type": "boolean",
                        "description": "Quantize the clip afterwards to repair send jitter",
                        "default": True,
                    },
                },
                "required": [
                    "track_index",
                    "slot_index",
                    "length_beats",
                    "bpm",
                    "notes",
                ],
            },
        ),
    ]


async def execute_tool(
    controller: BitwigOSCController, name: str, arguments: Dict[str, Any]
) -> List[TextContent]:
    """Execute a Bitwig tool

    Args:
        controller: BitwigOSCController instance
        name: Tool name to execute
        arguments: Tool arguments

    Returns:
        List of TextContent with results

    Raises:
        ValueError: If tool name is unknown or arguments are invalid
    """
    try:
        if name == "transport_play":
            controller.client.play()
            return [TextContent(type="text", text="Transport play/pause toggled")]

        elif name == "set_tempo":
            bpm = arguments.get("bpm")
            if bpm is None:
                raise ValueError("Missing required argument: bpm")

            if not isinstance(bpm, (int, float)) or bpm < 0 or bpm > 666:
                raise ValueError("Invalid tempo value: must be between 0 and 666")

            controller.client.set_tempo(bpm)
            return [TextContent(type="text", text=f"Tempo set to {bpm} BPM")]

        elif name == "set_track_volume":
            track_index = arguments.get("track_index")
            volume = arguments.get("volume")

            if track_index is None or volume is None:
                raise ValueError("Missing required arguments: track_index, volume")

            if not isinstance(track_index, int) or track_index < 1:
                raise ValueError("Invalid track_index: must be a positive integer")

            if not isinstance(volume, (int, float)) or volume < 0 or volume > 128:
                raise ValueError("Invalid volume: must be between 0 and 128")

            controller.client.set_track_volume(track_index, volume)
            return [
                TextContent(
                    type="text", text=f"Track {track_index} volume set to {volume}"
                )
            ]

        elif name == "set_track_pan":
            track_index = arguments.get("track_index")
            pan = arguments.get("pan")

            if track_index is None or pan is None:
                raise ValueError("Missing required arguments: track_index, pan")

            if not isinstance(track_index, int) or track_index < 1:
                raise ValueError("Invalid track_index: must be a positive integer")

            if not isinstance(pan, (int, float)) or pan < 0 or pan > 128:
                raise ValueError("Invalid pan: must be between 0 and 128")

            controller.client.set_track_pan(track_index, pan)
            return [
                TextContent(type="text", text=f"Track {track_index} pan set to {pan}")
            ]

        elif name == "toggle_track_mute":
            track_index = arguments.get("track_index")

            if track_index is None:
                raise ValueError("Missing required argument: track_index")

            if not isinstance(track_index, int) or track_index < 1:
                raise ValueError("Invalid track_index: must be a positive integer")

            controller.client.toggle_track_mute(track_index)
            return [TextContent(type="text", text=f"Track {track_index} mute toggled")]

        elif name == "set_device_parameter":
            param_index = arguments.get("param_index")
            value = arguments.get("value")

            if param_index is None or value is None:
                raise ValueError("Missing required arguments: param_index, value")

            if not isinstance(param_index, int) or param_index < 1:
                raise ValueError("Invalid param_index: must be a positive integer")

            if not isinstance(value, (int, float)) or value < 0 or value > 128:
                raise ValueError("Invalid value: must be between 0 and 128")

            controller.client.set_device_parameter(param_index, value)
            return [
                TextContent(
                    type="text", text=f"Device parameter {param_index} set to {value}"
                )
            ]

        elif name == "toggle_device_bypass":
            controller.client.toggle_device_bypass()
            return [TextContent(type="text", text="Device bypass toggled")]

        elif name == "select_device_sibling":
            sibling_index = arguments.get("sibling_index")

            if sibling_index is None:
                raise ValueError("Missing required argument: sibling_index")

            if (
                not isinstance(sibling_index, int)
                or sibling_index < 1
                or sibling_index > 8
            ):
                raise ValueError("Invalid sibling_index: must be between 1 and 8")

            controller.client.select_device_sibling(sibling_index)
            return [
                TextContent(
                    type="text", text=f"Selected sibling device {sibling_index}"
                )
            ]

        elif name == "navigate_device":
            direction = arguments.get("direction")

            if direction is None:
                raise ValueError("Missing required argument: direction")

            if direction not in ["next", "previous"]:
                raise ValueError("Invalid direction: must be 'next' or 'previous'")

            controller.client.navigate_device(direction)
            return [TextContent(type="text", text=f"Navigated to {direction} device")]

        elif name == "enter_device_layer":
            layer_index = arguments.get("layer_index")

            if layer_index is None:
                raise ValueError("Missing required argument: layer_index")

            if not isinstance(layer_index, int) or layer_index < 1 or layer_index > 8:
                raise ValueError("Invalid layer_index: must be between 1 and 8")

            controller.client.enter_device_layer(layer_index)
            return [
                TextContent(type="text", text=f"Entered device layer {layer_index}")
            ]

        elif name == "exit_device_layer":
            controller.client.exit_device_layer()
            return [TextContent(type="text", text="Exited device layer")]

        elif name == "toggle_device_window":
            controller.client.toggle_device_window()
            return [TextContent(type="text", text="Device window toggled")]

        # Browser tools
        elif name == "browse_insert_device":
            position = arguments.get("position", "after")

            if position not in ["after", "before"]:
                raise ValueError("Invalid position: must be 'after' or 'before'")

            controller.client.browse_for_device(position)
            return [
                TextContent(
                    type="text",
                    text=f"Browser opened to insert device {position} selected device",
                )
            ]

        elif name == "browse_device_presets":
            controller.client.browse_for_preset()
            return [
                TextContent(type="text", text="Browser opened to browse device presets")
            ]

        elif name == "commit_browser_selection":
            controller.client.commit_browser_selection()
            return [TextContent(type="text", text="Browser selection committed")]

        elif name == "cancel_browser":
            controller.client.cancel_browser()
            return [TextContent(type="text", text="Browser session canceled")]

        elif name == "navigate_browser_tab":
            direction = arguments.get("direction")

            if direction is None:
                raise ValueError("Missing required argument: direction")

            # Convert direction to "+" or "-"
            if direction == "next":
                dir_symbol = "+"
            elif direction == "previous":
                dir_symbol = "-"
            else:
                raise ValueError("Invalid direction: must be 'next' or 'previous'")

            controller.client.navigate_browser_tab(dir_symbol)
            return [
                TextContent(type="text", text=f"Navigated to {direction} browser tab")
            ]

        elif name == "navigate_browser_filter":
            filter_index = arguments.get("filter_index")
            direction = arguments.get("direction")

            if filter_index is None or direction is None:
                raise ValueError("Missing required arguments: filter_index, direction")

            if (
                not isinstance(filter_index, int)
                or filter_index < 1
                or filter_index > 6
            ):
                raise ValueError("Invalid filter_index: must be between 1 and 6")

            # Convert direction to "+" or "-"
            if direction == "next":
                dir_symbol = "+"
            elif direction == "previous":
                dir_symbol = "-"
            else:
                raise ValueError("Invalid direction: must be 'next' or 'previous'")

            controller.client.navigate_browser_filter(filter_index, dir_symbol)
            return [
                TextContent(
                    type="text",
                    text=f"Navigated to {direction} option in filter {filter_index}",
                )
            ]

        elif name == "reset_browser_filter":
            filter_index = arguments.get("filter_index")

            if filter_index is None:
                raise ValueError("Missing required argument: filter_index")

            if (
                not isinstance(filter_index, int)
                or filter_index < 1
                or filter_index > 6
            ):
                raise ValueError("Invalid filter_index: must be between 1 and 6")

            controller.client.reset_browser_filter(filter_index)
            return [TextContent(type="text", text=f"Reset filter {filter_index}")]

        elif name == "navigate_browser_result":
            direction = arguments.get("direction")

            if direction is None:
                raise ValueError("Missing required argument: direction")

            # Convert direction to "+" or "-"
            if direction == "next":
                dir_symbol = "+"
            elif direction == "previous":
                dir_symbol = "-"
            else:
                raise ValueError("Invalid direction: must be 'next' or 'previous'")

            controller.client.navigate_browser_result(dir_symbol)
            return [
                TextContent(
                    type="text", text=f"Navigated to {direction} browser result"
                )
            ]

        elif name == "device_browser_workflow":
            position = arguments.get("position", "after")
            num_tab_navigations = arguments.get("num_tab_navigations", 0)
            filter_navigations = arguments.get("filter_navigations", [])
            result_navigations = arguments.get("result_navigations", 0)

            # Validate parameters
            if position not in ["after", "before"]:
                raise ValueError("Invalid position: must be 'after' or 'before'")

            if not isinstance(num_tab_navigations, int):
                raise ValueError("Invalid num_tab_navigations: must be an integer")

            if not isinstance(result_navigations, int):
                raise ValueError("Invalid result_navigations: must be an integer")

            # Convert filter_navigations to the format required by browse_and_insert_device
            filter_nav_list = []
            if filter_navigations:
                for filter_nav in filter_navigations:
                    filter_index = filter_nav.get("filter_index")
                    steps = filter_nav.get("steps")

                    if filter_index is None or steps is None:
                        raise ValueError(
                            "Filter navigation missing filter_index or steps"
                        )

                    if (
                        not isinstance(filter_index, int)
                        or filter_index < 1
                        or filter_index > 6
                    ):
                        raise ValueError(
                            f"Invalid filter_index: {filter_index} must be between 1 and 6"
                        )

                    if not isinstance(steps, int):
                        raise ValueError(f"Invalid steps: {steps} must be an integer")

                    filter_nav_list.append((filter_index, steps))

            # Execute the workflow
            # Open device browser
            controller.client.browse_for_device(position)

            # Navigate through tabs
            for _ in range(abs(num_tab_navigations)):
                direction = "+" if num_tab_navigations >= 0 else "-"
                controller.client.navigate_browser_tab(direction)

            # Apply filter selections
            if filter_nav_list:
                for filter_index, steps in filter_nav_list:
                    for _ in range(abs(steps)):
                        direction = "+" if steps >= 0 else "-"
                        controller.client.navigate_browser_filter(
                            filter_index, direction
                        )

            # Navigate through results
            for _ in range(abs(result_navigations)):
                direction = "+" if result_navigations >= 0 else "-"
                controller.client.navigate_browser_result(direction)

            # Commit selection
            controller.client.commit_browser_selection()

            return [
                TextContent(
                    type="text", text="Device browser workflow completed successfully"
                )
            ]

        elif name == "preset_browser_workflow":
            filter_navigations = arguments.get("filter_navigations", [])
            result_navigations = arguments.get("result_navigations", 0)

            # Validate parameters
            if not isinstance(result_navigations, int):
                raise ValueError("Invalid result_navigations: must be an integer")

            # Convert filter_navigations to the format required by browse_and_load_preset
            filter_nav_list = []
            if filter_navigations:
                for filter_nav in filter_navigations:
                    filter_index = filter_nav.get("filter_index")
                    steps = filter_nav.get("steps")

                    if filter_index is None or steps is None:
                        raise ValueError(
                            "Filter navigation missing filter_index or steps"
                        )

                    if (
                        not isinstance(filter_index, int)
                        or filter_index < 1
                        or filter_index > 6
                    ):
                        raise ValueError(
                            f"Invalid filter_index: {filter_index} must be between 1 and 6"
                        )

                    if not isinstance(steps, int):
                        raise ValueError(f"Invalid steps: {steps} must be an integer")

                    filter_nav_list.append((filter_index, steps))

            # Execute the workflow
            # Open preset browser
            controller.client.browse_for_preset()

            # Apply filter selections
            if filter_nav_list:
                for filter_index, steps in filter_nav_list:
                    for _ in range(abs(steps)):
                        direction = "+" if steps >= 0 else "-"
                        controller.client.navigate_browser_filter(
                            filter_index, direction
                        )

            # Navigate through results
            for _ in range(abs(result_navigations)):
                direction = "+" if result_navigations >= 0 else "-"
                controller.client.navigate_browser_result(direction)

            # Commit selection
            controller.client.commit_browser_selection()

            return [
                TextContent(
                    type="text", text="Preset browser workflow completed successfully"
                )
            ]

        # Device browser index tools
        elif name == "search_device_browser":
            query = arguments.get("query")
            if not query:
                raise ValueError("Missing required argument: query")

            num_results = arguments.get("num_results", 5)
            category = arguments.get("category")
            type_filter = arguments.get("type")
            creator = arguments.get("creator")

            # Initialize the recommender
            index_dir = os.path.join(Path.home(), "bitwig_browser_index")
            recommender = BitwigDeviceRecommender(persistent_dir=index_dir)

            # Build filter dictionary
            filter_options = {}
            if category:
                filter_options["category"] = category
            if type_filter:
                filter_options["type"] = type_filter
            if creator:
                filter_options["creator"] = creator

            # Use None if no filters
            if not filter_options:
                filter_options = None

            # Search for devices
            try:
                # Check if index exists
                if recommender.indexer.get_device_count() == 0:
                    return [
                        TextContent(
                            type="text",
                            text="The device index has not been built yet. Please run bitwig-browser-index to build it.",
                        )
                    ]

                results = recommender.indexer.search_devices(
                    query=query, n_results=num_results, filter_options=filter_options
                )

                # Format results
                response_lines = [f"Search results for: {query}"]
                response_lines.append("")

                for i, result in enumerate(results, 1):
                    response_lines.append(f"{i}. {result['name']}")
                    response_lines.append(f"   Category: {result['category']}")
                    response_lines.append(f"   Type: {result['type']}")
                    response_lines.append(f"   Creator: {result['creator']}")
                    if result.get("tags"):
                        response_lines.append(f"   Tags: {', '.join(result['tags'])}")
                    if result.get("description"):
                        # Truncate long descriptions
                        desc = result["description"]
                        if len(desc) > 200:
                            desc = desc[:200] + "..."
                        response_lines.append(f"   Description: {desc}")
                    response_lines.append("")

                return [TextContent(type="text", text="\n".join(response_lines))]

            except Exception as e:
                logger.exception(f"Error searching device browser: {e}")
                return [
                    TextContent(
                        type="text", text=f"Error searching device browser: {str(e)}"
                    )
                ]

        elif name == "recommend_devices":
            description = arguments.get("description")
            if not description:
                raise ValueError("Missing required argument: description")

            num_results = arguments.get("num_results", 5)
            category = arguments.get("category")

            # Initialize the recommender
            index_dir = os.path.join(Path.home(), "bitwig_browser_index")
            recommender = BitwigDeviceRecommender(persistent_dir=index_dir)

            try:
                # Check if index exists
                if recommender.indexer.get_device_count() == 0:
                    return [
                        TextContent(
                            type="text",
                            text="The device index has not been built yet. Please run bitwig-browser-index to build it.",
                        )
                    ]

                recommendations = recommender.recommend_devices(
                    task_description=description,
                    num_results=num_results,
                    filter_category=category,
                )

                # Format recommendations
                response_lines = [f"Recommended devices for: {description}"]
                response_lines.append("")

                for i, rec in enumerate(recommendations, 1):
                    response_lines.append(f"{i}. {rec['device']} ({rec['category']})")
                    response_lines.append(f"   Creator: {rec['creator']}")
                    response_lines.append(f"   Relevance: {rec['relevance_score']:.2f}")
                    response_lines.append(f"   Why: {rec['explanation']}")
                    if rec.get("description"):
                        # Truncate long descriptions
                        desc = rec["description"]
                        if len(desc) > 150:
                            desc = desc[:150] + "..."
                        response_lines.append(f"   Description: {desc}")
                    response_lines.append("")

                return [TextContent(type="text", text="\n".join(response_lines))]

            except Exception as e:
                logger.exception(f"Error recommending devices: {e}")
                return [
                    TextContent(
                        type="text", text=f"Error recommending devices: {str(e)}"
                    )
                ]

        elif name == "get_device_categories":
            # Initialize the recommender
            index_dir = os.path.join(Path.home(), "bitwig_browser_index")
            recommender = BitwigDeviceRecommender(persistent_dir=index_dir)

            try:
                # Check if index exists
                if recommender.indexer.get_device_count() == 0:
                    return [
                        TextContent(
                            type="text",
                            text="The device index has not been built yet. Please run bitwig-browser-index to build it.",
                        )
                    ]

                # Get stats including categories
                stats = recommender.indexer.get_collection_stats()

                # Format response
                response_lines = ["Available Device Categories:"]
                response_lines.append("")

                for category in stats.get("categories", []):
                    response_lines.append(f"- {category}")

                response_lines.append("")
                response_lines.append("Available Device Types:")
                response_lines.append("")

                for type_ in stats.get("types", []):
                    response_lines.append(f"- {type_}")

                response_lines.append("")
                response_lines.append("Available Creators:")
                response_lines.append("")

                for creator in stats.get("creators", []):
                    response_lines.append(f"- {creator}")

                return [TextContent(type="text", text="\n".join(response_lines))]

            except Exception as e:
                logger.exception(f"Error getting device categories: {e}")
                return [
                    TextContent(
                        type="text", text=f"Error getting device categories: {str(e)}"
                    )
                ]

        elif name == "get_device_info":
            device_name = arguments.get("device_name")
            if not device_name:
                raise ValueError("Missing required argument: device_name")

            # Initialize the recommender
            index_dir = os.path.join(Path.home(), "bitwig_browser_index")
            recommender = BitwigDeviceRecommender(persistent_dir=index_dir)

            try:
                # Check if index exists
                if recommender.indexer.get_device_count() == 0:
                    return [
                        TextContent(
                            type="text",
                            text="The device index has not been built yet. Please run bitwig-browser-index to build it.",
                        )
                    ]

                # Search for the exact device
                results = recommender.indexer.search_devices(
                    query=device_name, n_results=10
                )

                # Find an exact match if possible
                exact_match = None
                for result in results:
                    if result["name"].lower() == device_name.lower():
                        exact_match = result
                        break

                if not exact_match and results:
                    # Use the closest match
                    exact_match = results[0]

                if exact_match:
                    # Format the device information
                    response_lines = [f"Device Information: {exact_match['name']}"]
                    response_lines.append("")
                    response_lines.append(f"Category: {exact_match['category']}")
                    response_lines.append(f"Type: {exact_match['type']}")
                    response_lines.append(f"Creator: {exact_match['creator']}")

                    if exact_match.get("tags"):
                        response_lines.append(f"Tags: {', '.join(exact_match['tags'])}")

                    if exact_match.get("description"):
                        response_lines.append("")
                        response_lines.append("Description:")
                        response_lines.append(exact_match["description"])

                    return [TextContent(type="text", text="\n".join(response_lines))]
                else:
                    return [
                        TextContent(
                            type="text",
                            text=f"No device found with name '{device_name}'",
                        )
                    ]

            except Exception as e:
                logger.exception(f"Error getting device info: {e}")
                return [
                    TextContent(
                        type="text", text=f"Error getting device info: {str(e)}"
                    )
                ]

        elif name == "add_track":
            track_type = arguments.get("track_type")
            if track_type not in ("instrument", "audio", "effect"):
                raise ValueError(
                    "Invalid track_type: must be instrument, audio or effect"
                )

            adders = {
                "instrument": controller.client.add_instrument_track,
                "audio": controller.client.add_audio_track,
                "effect": controller.client.add_effect_track,
            }
            adders[track_type]()
            return [TextContent(type="text", text=f"Added {track_type} track")]

        elif name == "set_track_recarm":
            track_index = arguments.get("track_index")
            armed = arguments.get("armed")

            if track_index is None or armed is None:
                raise ValueError("Missing required arguments: track_index, armed")

            controller.client.set_track_recarm(track_index, bool(armed))
            state = "armed" if armed else "disarmed"
            return [TextContent(type="text", text=f"Track {track_index} {state}")]

        elif name == "create_clip":
            track_index = arguments.get("track_index")
            slot_index = arguments.get("slot_index")
            beats = arguments.get("beats")

            if track_index is None or slot_index is None or beats is None:
                raise ValueError(
                    "Missing required arguments: track_index, slot_index, beats"
                )

            controller.client.create_clip(track_index, slot_index, beats)
            return [
                TextContent(
                    type="text",
                    text=(
                        f"Created {beats}-beat clip on track {track_index} "
                        f"slot {slot_index}"
                    ),
                )
            ]

        elif name == "launch_clip":
            track_index = arguments.get("track_index")
            slot_index = arguments.get("slot_index")

            if track_index is None or slot_index is None:
                raise ValueError("Missing required arguments: track_index, slot_index")

            controller.client.launch_clip(track_index, slot_index)
            return [
                TextContent(
                    type="text",
                    text=f"Launched clip on track {track_index} slot {slot_index}",
                )
            ]

        elif name == "launch_scene":
            scene_index = arguments.get("scene_index")
            if scene_index is None:
                raise ValueError("Missing required argument: scene_index")

            controller.client.launch_scene(scene_index)
            return [TextContent(type="text", text=f"Launched scene {scene_index}")]

        elif name == "quantize_clip":
            controller.client.quantize_clip()
            return [TextContent(type="text", text="Quantized selected clip")]

        elif name == "set_metronome":
            enabled = arguments.get("enabled")
            if enabled is None:
                raise ValueError("Missing required argument: enabled")

            controller.client.set_click(bool(enabled))
            state = "on" if enabled else "off"
            return [TextContent(type="text", text=f"Metronome {state}")]

        elif name == "set_time_signature":
            signature = arguments.get("signature")
            if not signature:
                raise ValueError("Missing required argument: signature")

            controller.client.set_time_signature(signature)
            return [TextContent(type="text", text=f"Time signature set to {signature}")]

        elif name == "play_note":
            note = arguments.get("note")
            if note is None:
                raise ValueError("Missing required argument: note")

            velocity = arguments.get("velocity", 100)
            duration = arguments.get("duration_seconds", 0.25)

            controller.client.note_on(note, velocity)
            await asyncio.sleep(duration)
            controller.client.note_off(note)
            return [TextContent(type="text", text=f"Played note {note}")]

        elif name == "record_pattern":
            track_index = arguments.get("track_index")
            slot_index = arguments.get("slot_index")
            length_beats = arguments.get("length_beats")
            bpm = arguments.get("bpm")
            notes = arguments.get("notes")

            if (
                track_index is None
                or slot_index is None
                or length_beats is None
                or bpm is None
                or notes is None
            ):
                raise ValueError(
                    "Missing required arguments: track_index, slot_index, "
                    "length_beats, bpm, notes"
                )

            if not isinstance(notes, list) or not notes:
                raise ValueError("notes must be a non-empty list")

            if not isinstance(bpm, (int, float)) or bpm <= 0:
                raise ValueError("bpm must be a positive number")

            seconds_per_beat = 60.0 / float(bpm)

            # Build the performance as an ordered list of note-on and note-off
            # events, so overlapping notes (chords) release correctly.
            events: List[tuple] = []
            for item in notes:
                pitch = item.get("note")
                start = item.get("start_beat")
                if pitch is None or start is None:
                    raise ValueError("each note needs 'note' and 'start_beat'")

                hold = item.get("length_beats", 0.5)
                velocity = item.get("velocity", 100)
                events.append((float(start), 1, int(pitch), int(velocity)))
                events.append((float(start) + float(hold), 0, int(pitch), 0))

            events.sort(key=lambda e: (e[0], e[1]))

            controller.client.create_clip(track_index, slot_index, length_beats)
            await asyncio.sleep(0.3)
            controller.client.set_track_recarm(track_index, True)
            await asyncio.sleep(0.2)
            controller.client.record_clip(track_index, slot_index)

            # Perform the notes against a monotonic clock, so jitter on one
            # event does not accumulate across the pattern.
            start_time = time.monotonic()
            for beat, is_on, pitch, velocity in events:
                target = start_time + beat * seconds_per_beat
                delay = target - time.monotonic()
                if delay > 0:
                    await asyncio.sleep(delay)

                if is_on:
                    controller.client.note_on(pitch, velocity)
                else:
                    controller.client.note_off(pitch)

            # Let the clip reach its end before stopping, so it loops cleanly.
            remaining = start_time + length_beats * seconds_per_beat - time.monotonic()
            if remaining > 0:
                await asyncio.sleep(remaining)

            controller.client.set_track_recarm(track_index, False)
            await asyncio.sleep(0.2)

            quantized = False
            if arguments.get("quantize", True):
                controller.client.quantize_clip()
                quantized = True

            return [
                TextContent(
                    type="text",
                    text=(
                        f"Recorded {len(notes)} notes into track {track_index} "
                        f"slot {slot_index} over {length_beats} beats at {bpm} BPM"
                        + (" (quantized)" if quantized else "")
                    ),
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.exception(f"Error executing tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]
