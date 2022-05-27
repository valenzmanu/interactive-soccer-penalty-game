import configparser
import logging
import os


class ConfigFileReader:
    CONFIG_FILE = "config.txt"

    @classmethod
    def read_game_window_configs(cls) -> dict:
        game_window_config = {"animations_paths": ("video_animations/GPO-ESTAS-LISTO.mp4",
                                                   "video_animations/GPO-GOL-SHORT.mp4",
                                                   "video_animations/GPO-FALLA-PENAL-SHORT.mp4"),
                              "window_size": (270, 210),
                              "window_start_position": (100, 100),
                              "fullscreen": False}
        try:
            config = configparser.ConfigParser()
            config.read(cls.CONFIG_FILE)
            
            if cls.CONFIG_FILE not in os.listdir():
                logging.warning(f'{cls.CONFIG_FILE} not found. Using default config: {game_window_config}')
                return game_window_config

            if "game-window" in config:
                game_window_config_items = config["game-window"]
                start_position_x = int(game_window_config_items["start-position-x"])
                start_position_y = int(game_window_config_items["start-position-y"])
                window_width = int(game_window_config_items["window-width"])
                window_height = int(game_window_config_items["window-height"])
                window_scale_factor = int(game_window_config_items["window-scale-factor"])
                fullscreen = game_window_config_items["fullscreen"] == "True"
                game_window_config["window_size"] = (
                    window_scale_factor * window_width, window_scale_factor * window_height)
                game_window_config["window_start_position"] = (start_position_x, start_position_y)
                game_window_config["fullscreen"] = fullscreen

            if "video-animations" in config:
                video_animations_config_items = config["video-animations"]
                ready_animation = video_animations_config_items["ready-animation"]
                goal_animation = video_animations_config_items["goal-animation"]
                fail_animation = video_animations_config_items["fail-animation"]
                animation_paths = (ready_animation, goal_animation, fail_animation)
                game_window_config["animations_paths"] = animation_paths

            logging.info(f'Successfully read game window config: {game_window_config}')

            return game_window_config

        except Exception as ex:
            logging.error(f'Unable to read game window config: {ex}')
            logging.info(f'Default game window config will be used: {game_window_config}')

        return game_window_config
