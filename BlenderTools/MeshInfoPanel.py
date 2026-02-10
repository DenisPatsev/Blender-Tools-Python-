bl_info = {
    "name": "Mesh info panel",
"Author": "Den Patsev",
    "version": (1, 0),
    "blender": (4, 5, 4),
    "location": "View3D > Sidebar > Active Mesh info"
}

import bpy

class MeshSubdivider(bpy.types.Operator):
    bl_idname = "mesh.subdivider"
    bl_label = "Subdivide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        current_mode = context.mode

        if current_mode != "EDIT":
            bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.mesh.subdivide(
            number_cuts=bpy.context.scene.subdivision_count,
            smoothness=0
        )

        bpy.ops.object.mode_set(mode = "OBJECT")

        self.report({'INFO'}, f"Subdivide by {bpy.context.scene.subdivision_count} fragments done")
        return {'FINISHED'}

class MeshInfoPanel(bpy.types.Panel):
    bl_idname = "MeshInfoPanel"
    bl_label = "Mesh info"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Custom Tools"

    @classmethod
    def poll(cls, context):
        return context.object


    def draw(self, context):
        obj = context.object
        mesh = obj.data
        layout = self.layout

        box = layout.box()
        name_row = box.row()
        name_row.label(text="Name")
        name_row.label(text=obj.name)
        box.separator(factor=2)

        if obj.type != 'MESH':
            layout.label(text="Not enough selected mesh")
            return

        vertices_info_row = box.row()
        vertices_info_row.label(text="Vertices")
        vertices_info_row.label(text=str(len(mesh.vertices)))

        edges_info_row = box.row()
        edges_info_row.label(text="Edges")
        edges_info_row.label(text=str(len(mesh.edges)))

        faces_info_row = box.row()
        faces_info_row.label(text="Faces")
        faces_info_row.label(text=str(len(mesh.polygons)))

        materials_info_row = box.row()
        materials_info_row.label(text="Materials")
        materials_info_row.label(text=str(len(mesh.materials)))

        subdivision_info = layout.box()
        subdivision_info.label(text="Subdivision")
        subdivision_info.prop(context.scene, "subdivision_count", text="Subdivisions Count")
        subdivision_info.operator(MeshSubdivider.bl_idname, text="Subdivide")

classes = (
        MeshInfoPanel, MeshSubdivider
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

bpy.types.Scene.subdivision_count = bpy.props.IntProperty(
    name="Subdivisions Count",
    min=0,
    max=8,
    default=1,
)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.subdivision_count

register()