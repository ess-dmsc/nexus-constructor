from geometry_constructor.data_model import Component, PixelGrid, PixelMapping, CountDirection, Corner


class NexusEncoder:
    """
    Wrapper class for methods used to transform properties from data_model classes to the format required by Nexus
    """

    @staticmethod
    def component_class_name(component: Component):
        return 'NX{}'.format(component.component_type.name.lower())

    @staticmethod
    def pixel_mapping(mapping: PixelMapping):
        """
        Returns a list of two item lists. Each sublist contains a face ID followed by the face's detector ID.
        Corresponds to the detector_faces dataset structure of the NXoff_geometry class.
        """
        return [[face_id, mapping.pixel_ids[face_id]]
                for face_id
                in range(len(mapping.pixel_ids))
                if mapping.pixel_ids[face_id] is not None]

    @staticmethod
    def pixel_grid_x_offsets(grid: PixelGrid):
        """
        Returns a list of 'row' lists of 'column' length.
        Each entry in the sublists are x positions of pixel instances in the given PixelGrid
        """
        return [[x * grid.col_width for x in range(grid.columns)]] * grid.rows

    @staticmethod
    def pixel_grid_y_offsets(grid: PixelGrid):
        """
        Returns a list of 'row' lists of 'column' length.
        Each entry in the sublists are y positions of pixel instances in the given PixelGrid
        """
        return [[y * grid.row_height] * grid.columns for y in range(grid.rows)]

    @staticmethod
    def pixel_grid_z_offsets(grid: PixelGrid):
        """
        Returns a list of 'row' lists of 'column' length.
        Each entry in the sublists are z positions of pixel instances in the given PixelGrid
        """
        return [[0] * grid.columns] * grid.rows

    @staticmethod
    def pixel_grid_detector_ids(grid: PixelGrid):
        """
        Returns a list of 'row' lists of 'column' length.
        Each entry in the sublists are detector id's of pixel instances in the given PixelGrid
        """

        ids = [[0] * grid.columns for _ in range(grid.rows)]

        for id_offset in range(grid.rows * grid.columns):
            # Determine a coordinate for the id based on the count direction from (0,0)
            if grid.count_direction == CountDirection.ROW:
                col = id_offset % grid.columns
                row = id_offset // grid.columns
            else:
                col = id_offset // grid.rows
                row = id_offset % grid.rows
            # Invert axes needed if starting in a different corner
            if grid.initial_count_corner in (Corner.TOP_LEFT, Corner.TOP_RIGHT):
                row = grid.rows - (1 + row)
            if grid.initial_count_corner in (Corner.TOP_RIGHT, Corner.BOTTOM_RIGHT):
                col = grid.columns - (1 + col)
            # Set the id at the calculated coordinate
            ids[row][col] = grid.first_id + id_offset

        return ids

    @staticmethod
    def ancestral_dependent_transform(component: Component):
        """
        Returns a string of the nexus location of the transform the given component is positioned relative to.
        """
        if component.transform_parent is None or component.transform_parent == component:
            dependent_on = '.'
        else:
            dependent_on = '.'
            dependent_found = False
            no_dependent = False
            ancestor = component.transform_parent
            index = -1
            if component.dependent_transform is not None:
                index = component.transform_parent.transforms.index(component.dependent_transform)
            while not (dependent_found or no_dependent):
                if len(ancestor.transforms) > 0:
                    dependent_on = '/entry/instrument/{}/{}'.format(ancestor.name,
                                                                    ancestor.transforms[index].name)
                    dependent_found = True
                elif ancestor.transform_parent is None or ancestor.transform_parent == ancestor:
                    no_dependent = True
                else:
                    if ancestor.dependent_transform is None:
                        index = -1
                    else:
                        index = component.transform_parent.transforms.index(component.dependent_transform)
                    ancestor = ancestor.transform_parent
        return dependent_on
