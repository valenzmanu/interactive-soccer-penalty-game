import configparser
import logging
import os


class ConfigFileReader:
    CONFIG_FILE = "config.txt"

    @classmethod
    def read_spot_files(cls) -> tuple:
        try:
            config = configparser.ConfigParser()
            config.read(cls.CONFIG_FILE)

            if "spots" in config:
                spots_paths = []
                for spot in config["spots"]:
                    spots_paths.append(spot)
                return tuple(spots_paths)

        except Exception as ex:
            logging.error(f"Unable to read spots {ex}")

    @classmethod
    def read_game_settings(cls) -> dict:
        game_settings = {"bar_velocity": 1}
        try:
            config = configparser.ConfigParser()
            config.read(cls.CONFIG_FILE)

            if cls.CONFIG_FILE not in os.listdir():
                logging.warning(f'{cls.CONFIG_FILE} not found. Using default config: {game_settings}')
                return game_settings

            if "game-settings" in config:
                game_settings["bar-velocity"] = int(config["game-settings"]["bar-velocity"])
                logging.info(f'Successfully read show_camera_window={game_settings}')
                return game_settings

        except Exception as ex:
            logging.error(f"Unable to read game settings {ex}")
        return game_settings

    @classmethod
    def read_show_camera_window(cls) -> bool:
        show_camera_window = True
        try:
            config = configparser.ConfigParser()
            config.read(cls.CONFIG_FILE)
            if cls.CONFIG_FILE not in os.listdir():
                logging.warning(f'{cls.CONFIG_FILE} not found. Using default source={show_camera_window}')
                return show_camera_window
            if "camera" in config:
                show_camera_window = config["camera"]["show-camera-window"] == "True"
                logging.info(f'Successfully read show_camera_window={show_camera_window}')
                return show_camera_window
        except Exception as ex:
            logging.error(f'Unable to read camera source: {ex}. Using default source={show_camera_window}')
        return show_camera_window

    @classmethod
    def read_camera_source(cls) -> int:
        source = 0
        try:
            config = configparser.ConfigParser()
            config.read(cls.CONFIG_FILE)
            if cls.CONFIG_FILE not in os.listdir():
                logging.warning(f'{cls.CONFIG_FILE} not found. Using default source={source}')
                return source
            if "camera" in config:
                source = int(config["camera"]["source"])
                logging.info(f'Successfully read source={source}')
                return source
        except Exception as ex:
            logging.error(f'Unable to read camera source: {ex}. Using default source={source}')
        return source

    @classmethod
    def read_camera_roi_configs(cls) -> dict:
        roi_configs = {"person_roi_w": 400,
                       "person_roi_h": 400,
                       "threshold_line_y": 350}

        try:
            config = configparser.ConfigParser()
            config.read(cls.CONFIG_FILE)
            if cls.CONFIG_FILE not in os.listdir():
                logging.warning(f'{cls.CONFIG_FILE} not found. Using default config: {roi_configs}')
                return roi_configs
            if "camera" in config:
                roi_configs["person_roi_w"] = int(config["camera"]["person-roi-w"])
                roi_configs["person_roi_h"] = int(config["camera"]["person-roi-h"])
                roi_configs["threshold_line_y"] = int(config["camera"]["threshold-line-y"])
                logging.info(f"Successfully read camera ROI configs: {roi_configs}")
            else:
                logging.warning(f"camera section not present in {cls.CONFIG_FILE}. Using default config: {roi_configs}")

            return roi_configs

        except Exception as ex:
            logging.error(f'Unable to read camera ROI config: {ex}')

        return roi_configs

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
