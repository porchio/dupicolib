"""This module contains higher-level code for board interfacing"""

from typing import Dict, final
import struct
from enum import Enum

import serial

from dupicolib.board_utilities import BoardUtilities
from dupicolib.hardware_board_commands import HardwareBoardCommands

class CommandCode(Enum):
    WRITE = 0
    READ = 1
    RESET = 2
    POWER = 3
    TEST = 5
    OSC_DET = 8

@final
class M3BoardCommands(HardwareBoardCommands):
    # The following map is used to associate a pin number (e.g. pin 1 or 10) on the socket
    # with the corresponding bit index used to access said pin by the dupico.
    # Negative numbers will be ignored in the mapping
    _PIN_NUMBER_TO_INDEX_MAP: Dict[int, int] = {
        1: 0, 2: 1, 3: 2,
        4: 3, 5: 4, 6: 5,
        7: 6, 8: 7, 9: 8,
        10: 9, 11: 10, 12: 11,
        13: 12, 14: 13, 15: 14,
        16: 15, 17: 16, 18: 17,
        19: 18, 20: 19, 22: 20,
        23: 21, 24: 22, 25: 23,
        26: 24, 27: 25, 28: 26,
        29: 27, 30: 28, 31: 29,
        32: 30, 33: 31, 34: 32,
        35: 33, 36: 34, 37: 35,
        38: 36, 39: 37, 40: 38,
        41: 39
    } | HardwareBoardCommands._get_basic_index_map() # Merge the pin mappings from the superclass

    @staticmethod
    def test_board(ser: serial.Serial) -> bool | None:
        """Perform a minimal self-test of the board

        Args:
            ser (serial.Serial): serial port on which to send the command

        Returns:
            bool | None: True if test passed correctly, False otherwise
        """        
        res: bytes | None = BoardUtilities.send_binary_command(ser, bytes([CommandCode.TEST.value]), 1)

        if res is not None:
            return res[0] == 1
        else:
            return None
        
    @staticmethod
    def set_power(state:bool, ser: serial.Serial) -> bool | None:
        """Enable or disable the power on the socket VCC

        Args:
            state (bool): True if we wish power applied, False otherwise
            ser (serial.Serial): serial port on which to send the command

        Returns:
            bool | None: True if power was applied, False otherwise, None in case we did not read the response correctly
        """
        res: bytes | None = BoardUtilities.send_binary_command(ser, bytes([CommandCode.POWER.value, 1 if state else 0]), 1)

        if res is not None:
            return res[0] == 1
        else:
            return None
        
    @staticmethod
    def write_pins(pins: int, ser: serial.Serial) -> int | None:
        """Toggle the specified pins and read their status back

        Args:
            pins (int): value that the pins will be set to. A bit set to '1' means that the pin will be pulled high
            ser (serial.Serial): serial port on which to send the command

        Returns:
            int | None: The value we read back from the pins, or None in case of parsing issues
        """                
        res: bytes | None = BoardUtilities.send_binary_command(ser, bytes([CommandCode.WRITE.value, *struct.pack('<Q', pins)]), 8)

        if res is not None:
            return struct.unpack('<Q', res)[0]
        else:
            return None
        
    @staticmethod
    def read_pins(ser: serial.Serial) -> int | None:
        """Read the value of the pins

        Args:
            ser (serial.Serial): serial port on which to send the command

        Returns:
            int | None: The value we read back from the pins, or None in case of parsing issues
        """        
        res: bytes | None = BoardUtilities.send_binary_command(ser, bytes([CommandCode.READ.value]), 8)

        if res is not None:
            return struct.unpack('<Q', res)[0]
        else:
            return None
        
    @staticmethod
    def detect_osc_pins(reads: int, ser: serial.Serial) -> int | None:
        """Repeat reads a number of times and reports which pins changed their state in at least one of the reads

        Args:
            tries (int): Number of reads to perform
            ser (serial.Serial | None, optional): serial port on which to send the command. Defaults to None.

        Returns:
            int | None: A bitmask with bits set to 1 for pins that were detected as flipping
        """        
        res: bytes | None = BoardUtilities.send_binary_command(ser, bytes([CommandCode.OSC_DET.value, reads & 0xFF]), 8)

        if res is not None:
            return struct.unpack('<Q', res)[0]
        else:
            return None
            
    @classmethod
    def map_value_to_pins(cls, pins: list[int], value: int) -> int:
        return cls._map_value_to_pins(cls._PIN_NUMBER_TO_INDEX_MAP, pins, value)
    
    @classmethod
    def map_pins_to_value(cls, pins: list[int], value: int) -> int:
        return cls._map_pins_to_value(cls._PIN_NUMBER_TO_INDEX_MAP, pins, value)