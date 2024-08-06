import json
import os

# JSON file path
json_file_path = r'C:\Users\anvit\Desktop\Downloads\DemoProject\DemoProject\testdb_structure.json'
current_dir = os.getcwd()
output_dir = os.path.join(current_dir, "DemoProject/src/main/java/com/example/DemoProject")
package_name = "com.example.DemoProject"

def generate_entities(schema, output_dir, package_name):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for table_name, table_info in schema.items():
            entity_name = table_name
            entity_content = f"""package {package_name}.model;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;

@Entity
public class {entity_name} {{
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    // Other columns
"""
            for column in table_info['columns']:
                column_name = column['name']
                column_type = column['type'].replace('NVARCHAR', 'String').replace('INT', 'Integer')
                entity_content += f"    private {column_type} {column_name};\n"
            entity_content += """
    // Getters and Setters
}
"""
            with open(os.path.join(output_dir, f"{entity_name}.java"), 'w') as file:
                file.write(entity_content)
    except Exception as e:
        print(f"Error generating entities: {e}")

def generate_repositories(schema, output_dir, package_name):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for table_name in schema.keys():
            repository_name = f"{table_name}Repository"
            repository_content = f"""package {package_name}.repository;

import {package_name}.model.{table_name};
import org.springframework.data.jpa.repository.JpaRepository;

public interface {repository_name} extends JpaRepository<{table_name}, Integer> {{
}}
"""
            with open(os.path.join(output_dir, f"{repository_name}.java"), 'w') as file:
                file.write(repository_content)
    except Exception as e:
        print(f"Error generating repositories: {e}")

def generate_resolvers(schema, output_dir, package_name):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for table_name in schema.keys():
            resolver_name = f"{table_name}Resolver"
            resolver_content = f"""package {package_name}.graphql.resolver;

import {package_name}.repository.{table_name}Repository;
import {package_name}.model.{table_name};
import graphql.schema.DataFetcher;
import graphql.schema.DataFetchingEnvironment;
import org.springframework.stereotype.Component;

@Component
public class {resolver_name} {{
    private final {table_name}Repository {table_name.lower()}Repository;

    public {resolver_name}({table_name}Repository {table_name.lower()}Repository) {{
        this.{table_name.lower()}Repository = {table_name.lower()}Repository;
    }}

    public DataFetcher<{table_name}> get{table_name}ById() {{
        return (DataFetchingEnvironment env) -> {{
            Integer id = env.getArgument("id");
            return {table_name.lower()}Repository.findById(id).orElse(null);
        }};
    }}

    public DataFetcher<List<{table_name}>> getAll{table_name}s() {{
        return (DataFetchingEnvironment env) -> {table_name.lower()}Repository.findAll();
    }}
}}
"""
            with open(os.path.join(output_dir, f"{resolver_name}.java"), 'w') as file:
                file.write(resolver_content)
    except Exception as e:
        print(f"Error generating resolvers: {e}")

def generate_graphql_controller(output_dir, package_name):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        controller_content = f"""package {package_name}.graphql.controller;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
import graphql.schema.GraphQLSchema;
import graphql.GraphQL;

@RestController
@RequestMapping("/graphql")
public class GraphQLController {{

    private final GraphQL graphQL;

    public GraphQLController(GraphQLSchema graphQLSchema) {{
        this.graphQL = GraphQL.newGraphQL(graphQLSchema).build();
    }}

    @RequestMapping(method = RequestMethod.POST)
    public Object executeGraphQL(String query) {{
        return graphQL.execute(query).getData();
    }}
}}
"""
        with open(os.path.join(output_dir, "GraphQLController.java"), 'w') as file:
            file.write(controller_content)
    except Exception as e:
        print(f"Error generating GraphQL controller: {e}")

def generate_graphql_schema(schema, output_path):
    try:
        graphql_schema = []

        for table_name, table_info in schema.items():
            graphql_type = f"type {table_name} {{\n"
            for column in table_info['columns']:
                column_name = column['name']
                column_type = column['type'].replace('NVARCHAR', 'String').replace('INT', 'Int')
                graphql_type += f"    {column_name}: {column_type}{'!' if not column['nullable'] else ''}\n"
            graphql_type += "}\n"
            graphql_schema.append(graphql_type)

        query_type = "type Query {\n"
        for table_name in schema.keys():
            query_type += f"    all{table_name}s: [{table_name}]\n"
            query_type += f"    {table_name.lower()}ById(id: Int!): {table_name}\n"
        query_type += "}\n"
        graphql_schema.append(query_type)

        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        with open(output_path, 'w') as f:
            f.write("\n".join(graphql_schema))
    except Exception as e:
        print(f"Error generating GraphQL schema: {e}")

# Main execution
def main():
    try:
        with open(json_file_path) as f:
            schema = json.load(f)

        generate_entities(schema, output_dir, package_name)
        generate_repositories(schema, output_dir, package_name)
        generate_resolvers(schema, output_dir, package_name)
        generate_graphql_controller(output_dir, package_name)
        generate_graphql_schema(schema, 'DemoProject/src/main/resources/graphql/schema.graphqls')

        print("Files generated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()



