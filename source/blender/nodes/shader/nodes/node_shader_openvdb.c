/*
 * ***** BEGIN GPL LICENSE BLOCK *****
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 * The Original Code is Copyright (C) 2015 Blender Foundation.
 * All rights reserved.
 *
 * The Original Code is: all of this file.
 *
 * Contributor(s): Kevin Dietrich
 *
 * ***** END GPL LICENSE BLOCK *****
 */

#include "../node_shader_util.h"

#include "openvdb_capi.h"

static bNodeSocketTemplate sh_node_openvdb_in[] = {
    {SOCK_VECTOR, 1, N_("Vector"), 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f, PROP_NONE, SOCK_HIDE_VALUE},
    {-1, 0, ""}
};

static void node_shader_init_openvdb(bNodeTree *UNUSED(ntree), bNode *node)
{
	NodeShaderOpenVDB *vdb = MEM_callocN(sizeof(NodeShaderOpenVDB), "NodeShaderOpenVDB");
	node->storage = vdb;
}

#ifdef WITH_OPENVDB
void ntreeUpdateOpenVDBNode(Main *bmain, bNodeTree *ntree, bNode *node)
{
	NodeShaderOpenVDB *vdb = node->storage;
	char *filename;

	if (!vdb) {
		return;
	}

	filename = &vdb->filename[0];

	if (BLI_path_is_rel(filename)) {
		BLI_path_abs(filename, bmain->name);
	}

	BLI_listbase_clear(&node->outputs);
	OpenVDB_getNodeSockets(filename, ntree, node);
}
#else
void ntreeUpdateOpenVDBNode(Main *bmain, bNodeTree *ntree, bNode *node)
{
	UNUSED_VARS(bmain, ntree, node);
}
#endif

void register_node_type_sh_openvdb(void)
{
	static bNodeType ntype;

	sh_node_type_base(&ntype, SH_NODE_OPENVDB, "OpenVDB Volume", NODE_CLASS_INPUT, 0);
	node_type_compatibility(&ntype, NODE_NEW_SHADING);
	node_type_size_preset(&ntype, NODE_SIZE_MIDDLE);
	node_type_socket_templates(&ntype, sh_node_openvdb_in, NULL);
	node_type_init(&ntype, node_shader_init_openvdb);
	node_type_storage(&ntype, "NodeShaderOpenVDB", node_free_standard_storage, node_copy_standard_storage);

	nodeRegisterType(&ntype);
}
