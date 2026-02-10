bl_info = {
    "name": "Кубогенератор",
    "author": "Ваше Имя",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Кубы",
    "description": "Создает N кубов в случайных позициях",
    "category": "Object",
}

import bpy

class CUBEGEN(bpy.types.Operator):
    bl_idname = "object.cubegen"
    bl_label = "Create cubes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        cubes_count = bpy.context.scene.cubes_count
        cube_size = bpy.context.scene.cube_size
        cubes_x_step = bpy.context.scene.cubes_x_step
        collection_name = f"Cubes_{cubes_count}"

        if collection_name not in bpy.data.collections:
            new_collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(new_collection)

        for i in range(cubes_count):
            cube = bpy.ops.mesh.primitive_cube_add(
                size=cube_size,
                location=(i * cubes_x_step, 0, 0),
                rotation=(0, 0, 0),
                scale=(1, 1, 1)
            )

            cube = bpy.context.active_object
            cube.name = f"Cube_{i}"

            if collection_name in bpy.data.collections:
                for col in cube.users_collection:
                    col.objects.unlink(cube)
                bpy.data.collections[collection_name].objects.link(cube)

        self.report({'INFO'}, f"Created{cubes_count} cubes")
        return {'FINISHED'}


class CUBEGEN_delete(bpy.types.Operator):
    bl_idname = "object.cubegen_delete"
    bl_label = "Delete cubes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        cubes_count = bpy.context.scene.cubes_count
        collection_name = f"Cubes_{cubes_count}"

        if collection_name not in bpy.data.collections:
            return{'FINISHED'}

        if collection_name in bpy.data.collections:
            coll = bpy.data.collections[collection_name]

            for obj in coll.objects:
                bpy.data.objects.remove(obj, do_unlink=True)

            bpy.data.collections.remove(coll)

        self.report({'INFO'}, f"All cubes deleted")
        return {'FINISHED'}

class CUBEGEN_panel(bpy.types.Panel):
    bl_label = "Cubes Generator"
    bl_idname = "object.cubegen_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Custom Tools"

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text = "Generations Settings", icon = 'MESH_CUBE')

        box.prop(context.scene, "cubes_count", text = "Count")
        box.prop(context.scene, "cube_size", text = "Size")
        box.prop(context.scene, "cubes_x_step", text = "X Step")

        row = layout.row()
        row.operator(CUBEGEN.bl_idname, text="create cubes", icon = 'ADD')
        row.operator(CUBEGEN_delete.bl_idname, text="delete cubes", icon = 'REMOVE')

classes = [CUBEGEN, CUBEGEN_panel, CUBEGEN_delete]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

bpy.types.Scene.cubes_count = bpy.props.IntProperty(
    name="Cube amount",
    description="How much cubes you want to create",
    default=1,
    min=1,
    max=100
)

bpy.types.Scene.cube_size = bpy.props.FloatProperty(
    name="Cube size",
    description="Size of the cube",
    default=1.0,
    min=0.1,
    max=10
)

bpy.types.Scene.cubes_x_step = bpy.props.IntProperty(
    name="Cube x step",
    description="Size of step by X axis",
    default=1,
    min=1,
    max=100
)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.cubes_count
    del bpy.types.Scene.cube_size
    del bpy.types.Scene.cubes_x_step

register()