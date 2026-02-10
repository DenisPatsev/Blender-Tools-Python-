
import bpy

class LODGenerator(bpy.types.Operator):
    bl_idname = "mesh.lod_generator"
    bl_label = "LOD Generator"

    def execute(self, context):
        scene = context.scene
        lod_count = scene.lod_count
        obj = context.active_object

        if(context.active_object != None):
            object_name = context.active_object.name


        if not context.active_object:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        for i in range(1, lod_count + 1):
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.duplicate()
            active_object = bpy.context.active_object
            active_object.location.y += active_object.scale.y * i * scene   .y_pos_offset
            modifier = active_object.modifiers.new(name="Decimate", type='DECIMATE')
            modifier.ratio = max(scene.min_lod_ratio, 1 - 1/(lod_count - i * 0.8))
            bpy.ops.object.modifier_apply(modifier=modifier.name)
            active_object.name = object_name + "_" + "LOD_" + str(i)
            active_object.select_set(False)

        obj.select_set(True)
        return {'FINISHED'}

class LODGeneratorPanel(bpy.types.Panel):
     bl_idname = "mesh.lod_generator_panel"
     bl_label = "LOD Generator"
     bl_space_type = "VIEW_3D"
     bl_region_type = "UI"
     bl_category = "Custom Tools"

     def draw(self, context):
         layout = self.layout
         obj = context.active_object

         object_name = layout.row(align=True)
         object_name.label(text="Object Name: ")

         if obj != None:
             object_name.label(text=obj.name)

         layout.separator()

         lod_count_row = layout.row(align=True)
         lod_count_row.label(text="LOD Count")
         lod_count_row.prop(context.scene, "lod_count")

         lod_ratio_row = layout.row(align=True)
         lod_ratio_row.label(text="Min LOD Ratio")
         lod_ratio_row.prop(context.scene, "min_lod_ratio")

         pos_offset_row = layout.row(align=True)
         pos_offset_row.label(text="Y Pos Offset")
         pos_offset_row.prop(context.scene, "y_pos_offset")

         layout.separator(factor=3)
         layout.operator("mesh.lod_generator", text="Generate LOD")

classes = (
        LODGeneratorPanel,
        LODGenerator
)

def register():
    bpy.types.Scene.lod_count = bpy.props.IntProperty(
        name="",
        default=0,
        min=0,
        max=4,
    )

    bpy.types.Scene.y_pos_offset = bpy.props.IntProperty(
        name="",
        default=0,
        min=0,
        max=100,
    )

    bpy.types.Scene.object_name = bpy.props.StringProperty(
        default="",
        name = ""
    )

    bpy.types.Scene.min_lod_ratio = bpy.props.FloatProperty(
        name="",
        default=0.1,
        min=0.01,
        max=1.0,
    )

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.lod_count
    del bpy.types.Scene.y_pos_offset
    del bpy.types.Scene.object_name
    del bpy.types.Scene.min_lod_ratio

register()