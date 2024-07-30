import json
import os
import shutil

from mappings import one_to_many, many_to_one
from conversions import camel_case, pascal_case, determine_primary_keys, map_sql_type_to_java

# Stores many to one relationships
many = dict()
# Stores one to many relationships
one = dict()

with open('db_structure.json', 'r') as file:
    db_structure = json.load(file)

# Function to generate ID class for Entity
def generate_id_class(db_structure, output_dir, table_index, primary_keys):
    table_name = list(db_structure.keys())[table_index]
    class_name = pascal_case(table_name)

    entity_dir = os.path.join(output_dir, 'entity')
    os.makedirs(entity_dir, exist_ok=True)

    # Generate class
    entity_path = os.path.join(entity_dir, f"{class_name}Id.java")
    
    with open(entity_path, 'w') as f:
        f.write(f"package {package_name}.entity;\n\n")
        
        f.write("import java.io.Serializable;\n")
        f.write(f"import java.util.Objects;\n\n")

        f.write(f"public class {class_name}Id implements Serializable {{\n")  
        for pk in primary_keys:
            f.write(f"private {pascal_case(many[pk]['reference_table'])} {camel_case(pk)};\n")

        # Getters
        for pk in primary_keys:
            f.write(f"public {pascal_case(many[pk]['reference_table'])} get{pascal_case(pk)}() {{\n")
            f.write(f"return this.{camel_case(pk)};\n")
            f.write("}\n\n")
        # Setters
        for pk in primary_keys:
            f.write(f"public void set{pascal_case(pk)} ({pascal_case(many[pk]['reference_table'])} {camel_case(pk)}) {{\n")
            f.write(f"this.{camel_case(pk)}={camel_case(pk)};\n")
            f.write("}\n\n")

        f.write("}")


# Function to generate the DTO class
def generate_dto_class(db_structure, output_dir, table_index, package_name):
    table_name = list(db_structure.keys())[table_index]
    details = db_structure[table_name]
    class_name = pascal_case(table_name)

    dto_dir = os.path.join(output_dir, 'dto')
    os.makedirs(dto_dir, exist_ok=True)

    # DTO class
    dto_path = os.path.join(dto_dir, f"{class_name}DTO.java")
    with open(dto_path, 'w') as f:
        f.write(f"package {package_name}.dto;\n\n")

        f.write(f"import {package_name}.entity.{class_name};\n")
        f.write("import java.util.List;\n")
        f.write("import java.util.stream.Collectors;\n\n")

        f.write(f"public class {class_name}DTO {{\n")
        for column in details["columns"]:
            column_name = column['name']
            column_type = column['type']
            java_type = map_sql_type_to_java(column_type)
            if column_name not in many:
                f.write(f"private {java_type} {camel_case(column_name)};\n")

        for column in one.keys():
            f.write(f"private List<{pascal_case(column)}DTO> {camel_case(column)};\n")

        f.write("\n") # Adds Empty line

        # No Args Constructor
        f.write(f"public {class_name}DTO() {{")
        f.write("}\n\n")       

        # convertToDTO() function
        f.write(f"public static {class_name}DTO convertToDTO({class_name} {camel_case(table_name)}) {{\n")
        f.write(f"{class_name}DTO {camel_case(table_name)}DTO = new {class_name}DTO();\n")
        for column in details['columns']:
            column_name = column['name']
            if column_name in many: continue
            f.write(f"{camel_case(table_name)}DTO.set{pascal_case(column_name)}({camel_case(table_name)}.get{pascal_case(column_name)}());\n")
        for column in one.keys():
            f.write(f"List<{pascal_case(column)}DTO> {camel_case(column)}DTO = {camel_case(table_name)}.get{pascal_case(column)}().stream().map({pascal_case(column)}DTO::convertToDTO).collect(Collectors.toList());\n")
            f.write(f"{camel_case(table_name)}DTO.set{pascal_case(column)}({camel_case(column)}DTO);\n")

        f.write(f"return {camel_case(table_name)}DTO;\n")
        f.write("}\n\n")

        # Getters and Setters
        for column in details['columns']:
            column_name = column['name']
            column_type = column['type']

            java_type = map_sql_type_to_java(column_type)
            camel_case_name = camel_case(column_name)

            # Getter
            if column_name in many:
                continue
            else: 
                f.write(f"public {java_type} get{pascal_case(column_name)}() {{\n")
            f.write(f"      return this.{camel_case_name};\n")
            f.write("}\n\n")

            # Setter
            if column_name in many:
                continue
            else: 
                f.write(f"public void set{pascal_case(column_name)}({java_type} {camel_case_name}) {{\n")
            f.write(f"      this.{camel_case_name} = {camel_case_name};\n")
            f.write("}\n\n")

        
        # Getter setter for one_to_many
        for column in one.keys():
            # Getter
            f.write(f"public List<{pascal_case(column)}DTO> get{pascal_case(column)}() {{\n")
            f.write(f"      return this.{camel_case(column)};\n")
            f.write("}\n\n")
            # Setter
            f.write(f"public void set{pascal_case(column)}(List<{pascal_case(column)}DTO> {camel_case(column)}) {{\n")
            f.write(f"      this.{camel_case(column)} = {camel_case(column)};\n")
            f.write("}\n\n")

        f.write("}\n")
        print(f"Generate DTO Class for {class_name}DTO")


# Function to generate the entity class
def generate_entity_class(db_structure, output_dir, table_index, package_name, schema):
    table_name = list(db_structure.keys())[table_index]
    details = db_structure[table_name]
    class_name = pascal_case(table_name)

    # Determine primary keys
    primary_keys = determine_primary_keys(details)
    print(f"Primary keys for {table_name}: {primary_keys}")

    # Create entity directory
    entity_dir = os.path.join(output_dir, 'entity')
    os.makedirs(entity_dir, exist_ok=True)

    # Generate Entity Class
    entity_path = os.path.join(entity_dir, f"{class_name}.java")
    
    with open(entity_path, 'w') as f:
        f.write(f"package {package_name}.entity;\n\n")

        f.write("import jakarta.persistence.*;\n")
        f.write(f"import java.util.*;\n\n")

        # Handle many-to-one relationships
        many = many_to_one(table_name)
        for key, fk in many.items():
            f.write(f"import {package_name}.entity.{pascal_case(fk['reference_table'])};\n")

        # Handle one-to-many relationships
        one = one_to_many(table_name)
        for tbl, columns in one.items():
            f.write(f"import {package_name}.entity.{pascal_case(tbl)};\n")

        f.write(f"\n@Entity\n@Table(name = \"{table_name}\", schema = \"{schema}\")\n")
        f.write(f"public class {class_name} {{\n")

        # Write fields
        for column in details["columns"]:
            column_name = column["name"]
            column_type = column["type"]
            if column_name in primary_keys:
                f.write(f"    @Id\n")
            f.write(f"    private {map_sql_type_to_java(column_type)} {camel_case(column_name)};\n")

        # Write relationships
        for tbl, columns in one.items():
            for col in columns:
                f.write(f"    @OneToMany(mappedBy = \"{camel_case(col[0])}\", cascade = CascadeType.ALL, fetch = FetchType.LAZY)\n")
                f.write(f"    private List<{pascal_case(tbl)}> {camel_case(tbl)}List;\n")

        for key, fk in many.items():
            f.write(f"    @ManyToOne(fetch = FetchType.LAZY)\n")
            f.write(f"    @JoinColumn(name = \"{key}\")\n")
            f.write(f"    private {pascal_case(fk['reference_table'])} {camel_case(fk['reference_table'])};\n")

        f.write("\n    // Getters and Setters\n")
        for column in details["columns"]:
            column_name = column["name"]
            java_field_type = map_sql_type_to_java(column["type"])
            f.write(f"    public {java_field_type} get{pascal_case(column_name)}() {{\n")
            f.write(f"        return {camel_case(column_name)};\n")
            f.write("    }\n\n")
            f.write(f"    public void set{pascal_case(column_name)}({java_field_type} {camel_case(column_name)}) {{\n")
            f.write(f"        this.{camel_case(column_name)} = {camel_case(column_name)};\n")
            f.write("    }\n\n")

        f.write("}\n")

        print(f"Entity class {class_name}.java generated successfully.")
        

# Function to generate the repository interface for the first table in the schema
def generate_repository_class(db_structure, output_dir, table_index, package_name):
    try:
        table_name = list(db_structure.keys())[table_index]
        class_name = pascal_case(table_name)
        # Create repository directory
        repository_dir = os.path.join(output_dir, 'repository')
        os.makedirs(repository_dir, exist_ok=True)
        print(f"Repository directory created: {repository_dir}")

        # Generate Repository Interface
        repository_path = os.path.join(repository_dir, f"{class_name}Repository.java")
        with open(repository_path, 'w') as f:
            f.write(f"package {package_name}.repository;\n\n")
            f.write(f"import org.springframework.data.jpa.repository.JpaRepository;\n")
            f.write(f"import {package_name}.entity.{class_name};\n\n")
            f.write(f"public interface {class_name}Repository extends JpaRepository<{class_name}, Long> {{\n")
            f.write("}\n")

        print(f"Repository interface {class_name}Repository.java created successfully.")

    except Exception as e:
        print(f"Error generating repository interface: {e}")

# Function to generate the service interface and implementation for the first table in the schema
def generate_service_classes(db_structure, output_dir, table_index, package_name):
    try:
        table_name = list(db_structure.keys())[table_index]
        class_name = pascal_case(table_name)

        # Create service directories
        service_dir = os.path.join(output_dir, 'service')
        service_impl_dir = os.path.join(service_dir, 'impl')
        os.makedirs(service_dir, exist_ok=True)
        os.makedirs(service_impl_dir, exist_ok=True)
        print(f"Service directories created: {service_dir}, {service_impl_dir}")

        # Generate Service Interface
        service_interface_path = os.path.join(service_dir, f"{class_name}Service.java")
        with open(service_interface_path, 'w') as f:
            f.write(f"package {package_name}.service;\n\n")
            f.write(f"import {package_name}.dto.{class_name}DTO; \n\n")
            f.write(f"import java.util.List;\n\n")
            f.write(f"public interface {class_name}Service {{\n")
            f.write(f"List<{class_name}DTO> findAll();\n")
            f.write(f"List<{class_name}DTO> findById(Long id);\n")
            f.write("}\n")

        print(f"Service interface {class_name}Service.java generated successfully.")

        # Generate Service Implementation
        service_impl_path = os.path.join(service_impl_dir, f"{class_name}ServiceImpl.java")
        with open(service_impl_path, 'w') as f:
            f.write(f"package {package_name}.service.impl;\n\n")

            f.write(f"import {package_name}.dto.{class_name}DTO;\n")
            f.write(f"import {package_name}.entity.{class_name};\n")
            f.write(f"import {package_name}.repository.{class_name}Repository;\n")
            f.write(f"import {package_name}.service.{class_name}Service;\n\n")

            f.write("import org.springframework.beans.factory.annotation.Autowired;\n")
            f.write("import org.springframework.stereotype.Service;\n\n")

            f.write("import java.util.List;\n")
            f.write("import java.util.stream.Collectors;\n\n")
            f.write("import java.util.Collections;\n")
            f.write("import java.util.List;\n")
            f.write("import java.util.Optional;\n")

            f.write(f"@Service\n")
            f.write(f"public class {class_name}ServiceImpl implements {class_name}Service {{\n\n")
            f.write(f"      @Autowired\n")
            f.write(f"      private {class_name}Repository {camel_case(table_name)}Repository;\n\n")

            f.write(f"      @Override\n")
            f.write(f"      public List<{class_name}DTO> findAll() {{\n")
            f.write(f"          List<{class_name}> {camel_case(table_name)} = {camel_case(table_name)}Repository.findAll();\n")
            f.write(f"          return {camel_case(table_name)}.stream().map({class_name}DTO::convertToDTO).collect(Collectors.toList());\n")
            f.write(f"      }}\n")

            f.write(f"      @Override\n")
            f.write(f"      public List<{class_name}DTO> findById(Long id){{\n")
            f.write(f"          Optional<{class_name}> {camel_case(table_name)} = {camel_case(table_name)}Repository.findById(id);\n")
            f.write(f"          return {camel_case(table_name)}.map(f -> Collections.singletonList({class_name}DTO.convertToDTO(f))).orElse(Collections.emptyList());\n")
            f.write("      }\n\n")
            

            f.write("}\n")

        print(f"Service implementation {class_name}ServiceImpl.java generated successfully.")

    except Exception as e:
        print(f"Error generating service classes: {e}")

# Function to generate the controller class for the first table in the schema
def generate_controller_class(db_structure, output_dir, table_index, package_name):
    try:
        table_name = list(db_structure.keys())[table_index]
        class_name = pascal_case(table_name)

        # Create controller directory
        controller_dir = os.path.join(output_dir, 'controller')
        os.makedirs(controller_dir, exist_ok=True)
        print(f"Controller directory created: {controller_dir}")

        # Generate Controller Class
        controller_path = os.path.join(controller_dir, f"{class_name}Controller.java")
        with open(controller_path, 'w') as f:
            f.write(f"package {package_name}.controller;\n\n")
            f.write(f"import {package_name}.dto.{class_name}DTO;\n")
            f.write(f"import {package_name}.service.{class_name}Service;\n")
            f.write(f"import org.springframework.beans.factory.annotation.Autowired;\n")
            f.write(f"import org.springframework.web.bind.annotation.GetMapping;\n")
            f.write(f"import org.springframework.web.bind.annotation.RequestMapping;\n")
            f.write(f"import org.springframework.web.bind.annotation.PathVariable;\n")
            f.write(f"import org.springframework.web.bind.annotation.RestController;\n\n")
            f.write(f"import java.util.List;\n\n")
            f.write(f"@RestController\n")
            f.write(f"@RequestMapping(\"{table_name}\")\n")
            f.write(f"public class {class_name}Controller {{\n\n")
            f.write(f"      @Autowired\n")
            f.write(f"      private {class_name}Service {camel_case(table_name)}Service;\n\n")
            f.write(f"      @GetMapping\n")
            f.write(f"      public List<{class_name}DTO> findAll() {{\n")
            f.write(f"          return {camel_case(table_name)}Service.findAll();\n")
            f.write("      }\n")
            f.write(r'      @GetMapping("/{id}")')
            f.write("\n")
            f.write(f"      public List<{class_name}DTO> findById(@PathVariable Long id){{\n")
            f.write(f"          List<{class_name}DTO> {camel_case(table_name)} = {camel_case(table_name)}Service.findById(id);\n")
            f.write(f"          return {camel_case(table_name)}.isEmpty() ? null : {camel_case(table_name)};\n")
            f.write("      }\n\n")

            f.write("}\n")

        print(f"Controller class {class_name}Controller.java generated successfully.")
    
    except Exception as e:
        print(f"Error generating controller class: {e}")
        

def generate_exception_mapper_class(output_dir, package_name):
    try:
        exception_dir = os.path.join(output_dir, 'exception')
        os.makedirs(exception_dir, exist_ok=True)

        exception_mapper_path = os.path.join(exception_dir, "ExceptionMapper.java")
        with open(exception_mapper_path, 'w') as f:
            f.write(f"package {package_name}.exception;\n\n")
            f.write("import org.springframework.http.HttpStatus;\n")
            f.write("import org.springframework.http.ResponseEntity;\n")
            f.write("import org.springframework.web.bind.annotation.ControllerAdvice;\n")
            f.write("import org.springframework.web.bind.annotation.ExceptionHandler;\n")
            f.write("import org.springframework.web.context.request.WebRequest;\n")
            f.write("import java.util.Date;\n\n")

            f.write("@ControllerAdvice\n")
            f.write("public class ExceptionMapper {\n\n")

            f.write("    @ExceptionHandler(ResourceNotFoundException.class)\n")
            f.write("    public ResponseEntity<ErrorDetails> handleResourceNotFoundException(ResourceNotFoundException ex, WebRequest request) {\n")
            f.write("        ErrorDetails errorDetails = new ErrorDetails(new Date(), ex.getMessage(), request.getDescription(false));\n")
            f.write("        return new ResponseEntity<>(errorDetails, HttpStatus.NOT_FOUND);\n")
            f.write("    }\n\n")

            f.write("    @ExceptionHandler(Exception.class)\n")
            f.write("    public ResponseEntity<ErrorDetails> handleGlobalException(Exception ex, WebRequest request) {\n")
            f.write("        ErrorDetails errorDetails = new ErrorDetails(new Date(), ex.getMessage(), request.getDescription(false));\n")
            f.write("        return new ResponseEntity<>(errorDetails, HttpStatus.INTERNAL_SERVER_ERROR);\n")
            f.write("    }\n\n")

            f.write("    public static class ErrorDetails {\n")
            f.write("        private Date timestamp;\n")
            f.write("        private String message;\n")
            f.write("        private String details;\n\n")

            f.write("        public ErrorDetails(Date timestamp, String message, String details) {\n")
            f.write("            super();\n")
            f.write("            this.timestamp = timestamp;\n")
            f.write("            this.message = message;\n")
            f.write("            this.details = details;\n")
            f.write("        }\n\n")

            f.write("        public Date getTimestamp() {\n")
            f.write("            return timestamp;\n")
            f.write("        }\n\n")

            f.write("        public String getMessage() {\n")
            f.write("            return message;\n")
            f.write("        }\n\n")

            f.write("        public String getDetails() {\n")
            f.write("            return details;\n")
            f.write("        }\n")
            f.write("    }\n")
            f.write("}\n")

        resource_not_found_exception_path = os.path.join(exception_dir, "ResourceNotFoundException.java")
        with open(resource_not_found_exception_path, 'w') as f:
            f.write(f"package {package_name}.exception;\n\n")
            f.write("public class ResourceNotFoundException extends RuntimeException {\n")
            f.write("    private static final long serialVersionUID = 1L;\n\n")
            f.write("    public ResourceNotFoundException(String message) {\n")
            f.write("        super(message);\n")
            f.write("    }\n\n")
            f.write("    public ResourceNotFoundException(String message, Throwable cause) {\n")
            f.write("        super(message, cause);\n")
            f.write("    }\n")
            f.write("}\n")

        print("Generated ExceptionMapper and ResourceNotFoundException classes successfully")
    except Exception as e:
        print(f"An error occurred while generating the exception classes: {e}")

# Define the output directory for generated classes
output_dir = "generated_classes"

# Define the package name for the generated classes
package_name = "com.example.demo"


# Generate ExceptionMapper class
generate_exception_mapper_class(output_dir, package_name)


def copy_files_to_destination(src_dir, dest_dir):
    # Check if source directory exists
    if not os.path.exists(src_dir):
        print(f"Source directory {src_dir} does not exist.")
        return 
    
    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    # Copy each file or directory in the source directory to the destination directory
    for filename in os.listdir(src_dir):
        src_path = os.path.join(src_dir, filename)
        dest_path = os.path.join(dest_dir, filename)
        try:
            if os.path.isfile(src_path):
                shutil.copy(src_path, dest_path)
            elif os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path)
        except Exception as e:
            print(f"Error copying {filename}: {e}")


####################################################################### Define output directory #######################################################################

current_dir = os.getcwd()
# output_dir_in = input("Enter output directory: ")
# output_dir = os.path.join(current_dir, output_dir_in)
# package_name_in = input("Enter package name: ")
# package_name = package_name_in
output_dir = os.path.join(current_dir, "src\main\java\com\example\DemoProject")
package_name = "com.example.DemoProject"

for table_index in range(len(db_structure)):

    table_name = list(db_structure.keys())[table_index]
    many = many_to_one(table_name)
    one = one_to_many(table_name)

    # Entity
    generate_entity_class(db_structure, output_dir, table_index, package_name, "DemoProject")
    print("Entity class generated successfully.")

    # DTO
    generate_dto_class(db_structure, output_dir, table_index, package_name)
    print("DTO class generated successfully.")

    # Repository
    generate_repository_class(db_structure, output_dir, table_index, package_name)
    print("Repository class generated successfully.")

    # Service
    generate_service_classes(db_structure, output_dir, table_index, package_name)
    print("Service class generated successfully.")

    # Controller
    generate_controller_class(db_structure, output_dir, table_index, package_name)
    print("Controller class generated successfully.")
    
    generate_exception_mapper_class(output_dir,package_name)
    print("ExceptionMapper class generated successfully.")

# Define source and destination libs
src_dir = os.path.join(current_dir, output_dir)
dest_dir = r"C:\Users\anvit\Desktop\Downloads\DemoProject\src\main\java\com\example\DemoProject"

# Call the function to copy the files
copy_files_to_destination(src_dir, dest_dir)
