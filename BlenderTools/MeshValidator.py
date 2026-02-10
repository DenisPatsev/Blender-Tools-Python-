import os.path

import bpy


class HandleDroppedAsset(bpy.types.Operator):
    bl_idname = "meshes.handle_dropper_asset"
    bl_label = "Handle Asset"

    asset_name: bpy.props.StringProperty()
    asset_type: bpy.props.StringProperty()
    file_path: bpy.props.StringProperty()
    mesh_validity: bpy.props.BoolProperty()

    def execute(self, context):
        objects_before = set(bpy.data.objects)

        if (self.asset_type == "FILE"):
            extention = os.path.splitext(self.file_path)[1].lower()

            if extention == ".fbx":
                bpy.ops.import_scene.fbx(filepath=self.file_path)
            elif extention == ".obj":
                bpy.ops.import_scene.obj(filepath=self.file_path)
            elif extention == ".blend":
                self.import_from_blend(self.file_path, context)
            else:
                self.report({"ERROR"}, "Invalid file extension")

        else:
            self.report({"ERROR"}, "File type not supported")

        objects_after = set(bpy.data.objects)

        new_objects = objects_after - objects_before

        new_objects_temp = []

        total_vertex_count = bpy.context.scene.total_vertex_count

        for obj in new_objects:
            temp_obj = bpy.data.objects.get(obj.name, obj)
            if obj.type == "MESH":
                new_objects_temp.append(temp_obj)
                mesh_data = obj.data

                vertex_count = len(mesh_data.vertices)
                total_vertex_count += vertex_count
                self.report({"INFO"}, "Vertex count: " + str(vertex_count))

        bpy.context.scene.total_vertex_count = total_vertex_count

        context.scene.objects_to_delete.clear()

        for obj in new_objects_temp:
            item = context.scene.objects_to_delete.add()
            item.name = obj.name

        if total_vertex_count > bpy.context.scene.target_vertex:
            bpy.context.scene.mesh_validity = False
            mat = self.create_red_material()

            for obj in new_objects_temp:
                obj.data.materials.clear()
                obj.data.materials.append(mat)

            self.report({"INFO"}, str(bpy.context.scene.mesh_validity))
        else:
            bpy.context.scene.mesh_validity = True
            self.report({"INFO"}, str(bpy.context.scene.mesh_validity))

        self.report({"INFO"}, "Total Vertex count: " + str(total_vertex_count))
        return {'FINISHED'}

    def import_from_blend(self, filepath, context):
        with bpy.data.libraries.load(filepath) as (data_input, data_otput):
            data_otput.meshes = data_input.meshes

        for mesh in data_otput.meshes:
            obj = bpy.data.objects.new(mesh.name, mesh)
            context.collection.objects.link(obj)

    def create_red_material(self):
        mat = bpy.data.materials.new(name="Red Material")
        mat.use_nodes = True

        mat_nodes = mat.node_tree.nodes
        mat_links = mat.node_tree.links

        mat_nodes.clear()

        output = mat_nodes.new(type="ShaderNodeOutputMaterial")
        principled = mat_nodes.new(type="ShaderNodeBsdfPrincipled")
        principled.inputs["Base Color"].default_value = (1, 0, 0, 1)
        principled.inputs["Roughness"].default_value = 1

        mat_links.new(principled.outputs['BSDF'], output.inputs['Surface'])

        return mat


class DeleteImportedObject(bpy.types.Operator):
    bl_idname = "object.delete_imported_object"
    bl_label = "Delete Imported Object"
    bl_description = "Delete Imported Object"

    def execute(self, context):
        obj_names_to_delete = []

        for obj in context.scene.objects_to_delete:
            obj_names_to_delete.append(obj.name)

        for obj_name in obj_names_to_delete:
            if obj_name in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)

        context.scene.objects_to_delete.clear()
        context.scene.total_vertex_count = 0
        context.scene.object_drag_field = ""
        context.scene.mesh_validity = False
        return {'FINISHED'}


class AssetValidatorPanel(bpy.types.Panel):
    bl_idname = "Asset_Validator_Panel"
    bl_label = "Asset Validator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Custom Tools"

    def draw(self, context):
        layout = self.layout

        object_field_row = layout.row(align=True)
        object_field_row.label(text="Object Path Field")
        object_field_row.prop(context.scene, "object_drag_field", text="")

        if context.scene.object_drag_field:
            filepath = context.scene.object_drag_field
            if os.path.exists(filepath):
                filename = os.path.basename(filepath)
                name_row = layout.row(align=True)
                name_row.label(text="File Name:")
                name_row.label(text=filename)
                operator = layout.operator("meshes.handle_dropper_asset", text="Import file", icon="IMPORT")
                operator.asset_type = 'FILE'
                operator.file_path = filepath
                layout.separator(factor=3)

        target_vertex_row = layout.row(align=True)
        target_vertex_row.label(text="Target Vertex")
        target_vertex_row.prop(context.scene, "target_vertex", text="")

        if not context.scene.object_drag_field == "":
            imported_vertex_row = layout.row()
            imported_vertex_row.label(text="Imported Mesh Vertex Count")
            imported_vertex_row.label(text=str(bpy.context.scene.total_vertex_count))
            layout.separator(factor=3)

            if context.scene.total_vertex_count > 0:
                if bpy.context.scene.mesh_validity:
                    layout.label(text="Object is valid")
                elif not bpy.context.scene.mesh_validity:
                    layout.label(text="Object is not valid")
                    layout.operator("object.delete_imported_object", text="Delete imported Objects")


class ImportedObject(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Object Name",
        description="Object Name"
    )


classes = (
    AssetValidatorPanel,
    HandleDroppedAsset,
    ImportedObject,
    DeleteImportedObject
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.target_vertex = bpy.props.IntProperty(
        name="Target Vertex",
        description="Target Vertex",
        default=1,
        min=1,
        max=10000
    )

    bpy.types.Scene.object_drag_field = bpy.props.StringProperty(
        name="Object Field",
        description="Object Field",
        subtype="FILE_PATH",
        default="",
    )

    bpy.types.Scene.mesh_validity = bpy.props.BoolProperty(
        name="Mesh Validity",
        description="Mesh Validity",
        default=False,
    )

    bpy.types.Scene.total_vertex_count = bpy.props.IntProperty(
        name="Total Vertex Count",
        description="Total Vertex Count",
        default=0,
    )

    bpy.types.Scene.objects_to_delete = bpy.props.CollectionProperty(
        type=ImportedObject,
        name="Objects",
    )


def unregister():
    del bpy.types.Scene.target_vertex
    del bpy.types.Scene.object_drag_field
    del bpy.types.Scene.mesh_validity
    del bpy.types.Scene.total_vertex_count
    del bpy.types.Scene.objects_to_delete

    for cls in classes:
        bpy.utils.unregister_class(cls)


register()
