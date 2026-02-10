import bpy
import bpy.types
import bpy.props

class FBXFastExporter(bpy.types.Operator):
    bl_idname = "object.fast_fbx_exporter"
    bl_label = "Fast Exporter"
    bl_description = "Exporter"

    def execute(self, context):

        bpy.ops.object.select_all(action="SELECT")


        bpy.ops.object.transform_apply(location = False, rotation = True, scale = True)

        bpy.ops.export_scene.fbx(
            filepath="D:\BlenderModels\\" + bpy.context.scene.file_path + ".fbx",
            check_existing=True,
            bake_anim=False,
            apply_unit_scale=True,
            apply_scale_options="FBX_SCALE_UNITS",
            object_types={'MESH'}
        )

        self.report({'INFO'}, "Export FBX File successful")
        return {"FINISHED"}

class ObjectsListItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name = "Name")
    scale_x: bpy.props.FloatProperty(name = "Scale X")
    scale_y: bpy.props.FloatProperty(name = "Scale Y")
    scale_z: bpy.props.FloatProperty(name = "Scale Z")

class ObjectsUIList(bpy.types.UIList):
    bl_idname = "OBJECT_UI_List"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index=0, flt_flag=0):

        column = layout.column(align=1)
        column.label(text="[ Name: " + item.name + "]")
        column.label(text=f"     Scale X: {item.scale_x:.3f}")
        column.label(text=f"     Scale Y: {item.scale_y:.3f}")
        column.label(text=f"     Scale Z: {item.scale_z:.3f}")
        column.separator(factor = 3)


class UpdateObjectsList(bpy.types.Operator):
    bl_idname = "object.update_objects_list"
    bl_label = "Update Objects List"

    def execute(self, context):
        objects_list = context.scene.objects_list

        objects_list.clear()

        for obj in context.scene.objects:
            item = objects_list.add()
            item.name = obj.name
            item.scale_x = obj.scale.x
            item.scale_y = obj.scale.y
            item.scale_z = obj.scale.z

        return {"FINISHED"}

class FBXFastExporterPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_fbx_fast_exporter_panel"
    bl_label = "FBX Fast Exporter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Custom Tools"

    def draw(self, context):
        layout = self.layout

        panel = layout.box()

        panel.template_list(
              "OBJECT_UI_List",
              "",
              context.scene,
              "objects_list",
              context.scene,
              "objects_list_index"
         )

        layout.separator()

        layout.prop(context.scene, "file_path", text="Filename")
        layout.operator("object.update_objects_list", text = "Update Objects List")
        layout.operator("object.fast_fbx_exporter", text = "Fast export")

classes = (ObjectsListItem, FBXFastExporterPanel, FBXFastExporter, ObjectsUIList, UpdateObjectsList)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.objects_list = bpy.props.CollectionProperty(type=ObjectsListItem)
    bpy.types.Scene.objects_list_index = bpy.props.IntProperty(default=0)
    bpy.types.Scene.file_path = bpy.props.StringProperty()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.objects_list
    del bpy.types.Scene.objects_list_index
    del bpy.types.Scene.file_path

register()
