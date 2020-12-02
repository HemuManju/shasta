from .primitive_manager import PrimitiveManager


class ActionManager(object):
    def __init__(self, state_manager, physics_client):
        self.config = state_manager.config
        self.state_manager = state_manager

        # Setup the platoons
        self._init_platoons_setup(physics_client)
        return None

    def _init_platoons_setup(self, physics_client):
        """Initial setup of platoons with primitive execution class.
            Each platoon name is given as uxv_p_* where * is the platoon number
            and x is either 'a' or 'g' depending on platoon type.
            The containers used for platoons are dict where key is uxv_p_*

            As an example one of the keys is 'uav_p_1'
            which is platoon 1 of type uav
        """
        self.uav_platoons = {}  # A container for platoons
        for i in range(self.config['simulation']['n_uav_platoons']):
            key = 'uav_p_' + str(i + 1)
            self.uav_platoons[key] = PrimitiveManager(self.state_manager,
                                                      physics_client)

        self.ugv_platoons = {}
        for i in range(self.config['simulation']['n_ugv_platoons']):
            key = 'ugv_p_' + str(i + 1)
            self.ugv_platoons[key] = PrimitiveManager(self.state_manager,
                                                      physics_client)
        return None

    def get_actions(self, attributes=None):
        """Returns the attributes of the primitive manager such as actions or
        specific attricutes such as centroid of platoons or target postiion

        Parameters
        ----------
        attributes : list
            A list of attributes to extract from the primitive manager.
            If this is empyt all the member variables
            from the primitive instance will be returned

        Returns
        -------
        dict
            A dictionary of all the attributes
            as specified by the 'attributes' input parameter
        """

        attribute = {}
        for i in range(self.config['simulation']['n_uav_platoons']):
            platoon_key = 'uav_p_' + str(i + 1)
            if attributes:
                attribute[platoon_key] = {
                    attr: vars(self.uav_platoons[platoon_key])['action'][attr]
                    for attr in attributes
                }
            else:
                attribute[platoon_key] = vars(
                    self.uav_platoons[platoon_key])['action']
        for i in range(self.config['simulation']['n_uav_platoons']):
            platoon_key = 'ugv_p_' + str(i + 1)
            if attributes:
                attribute[platoon_key] = {
                    attr: vars(self.ugv_platoons[platoon_key])['action'][attr]
                    for attr in attributes
                }
            else:
                attribute[platoon_key] = vars(
                    self.ugv_platoons[platoon_key])['action']
        return attribute

    def get_allocated_vehicle(self, n_vehicles, vehicles_type):
        """Allocated the vehicles to the platoons as required

        Parameters
        ----------
        n_vehicles : int
            Number of vehicles in the platoon
        vehicles_type : str
            Type of vehicles 'uav' or 'ugv'

        Returns
        -------
        vehicles_id: list
            A list of vehicles_id assigned to a platoon
        vehicles: list
            A list of vehicle instance of uav or ugv
        """
        vehicles, vehicles_id = [], []
        if vehicles_type == 'uav':
            for uav in self.state_manager.uav:
                if uav.idle and uav.functional:
                    vehicles.append(uav)
                    vehicles_id.append(uav.vehicle_id)
                    uav.idle = False  # Once allocated they are non-idles

                if len(vehicles) == n_vehicles:
                    break
        else:
            for ugv in self.state_manager.ugv:
                if ugv.idle and ugv.functional:
                    vehicles.append(ugv)
                    vehicles_id.append(ugv.vehicle_id)
                    ugv.idle = False  # Once allocated they are non-idles

                if len(vehicles) == n_vehicles:
                    break

        return vehicles_id, vehicles

    def perform_action_allocation(self, actions_uav, actions_ugv):
        """Perfroms action allocation and

            Parameters
            ----------
            actions_uav : dict
                UAV decoded actions
            actions_ugv : dict
                UGV decoded actions
            """
        # UAV Actions
        for key in actions_uav:
            n_vehicles = actions_uav[key]['n_vehicles']

            # Allocate only when there are more than 0 vehicles
            if n_vehicles < 1:
                actions_uav[key]['execute'] = False
            else:
                # Perform vehicle allocation
                vehicles_id, vehicles = self.get_allocated_vehicle(
                    n_vehicles, vehicles_type='uav')

                # Update actions
                actions_uav[key]['vehicles_id'] = vehicles_id
                actions_uav[key]['vehicles'] = vehicles

            # Allocate
            self.uav_platoons[key].allocate_action(actions_uav[key])

        # UGV actions
        for key in actions_ugv:
            n_vehicles = actions_ugv[key]['n_vehicles']

            # Allocate only when there are more than 0 vehicles
            if n_vehicles < 1:
                actions_ugv[key]['execute'] = False
            else:
                # Perform vehicle allocation
                vehicles_id, vehicles = self.get_allocated_vehicle(
                    n_vehicles, vehicles_type='ugv')

                # Update actions
                actions_ugv[key]['vehicles_id'] = vehicles_id
                actions_ugv[key]['vehicles'] = vehicles

            # Allocate
            self.ugv_platoons[key].allocate_action(actions_ugv[key])
        return None

    def primitive_execution(self):
        """Performs task execution

        Parameters
        ----------
        actions_uav : array
            UAV decoded actions
        actions_ugv : array
            UAV decoded actions
        hand_coded : bool
            Whether hand coded tactics are being used or not
        """
        primitives_done = []

        # Update all the ugv vehicles
        for _, platoon in self.ugv_platoons.items():
            done = platoon.execute_primitive()
            primitives_done.append(done)

        # Update all the uav vehicles
        for _, platoon in self.uav_platoons.items():
            done = platoon.execute_primitive()
            primitives_done.append(done)

        if all(primitives_done):
            done_rolling = True
        else:
            done_rolling = False

        return done_rolling
