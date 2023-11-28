Vue.component('select2', {
  props: ['options', 'value'],
  mounted: function() {
    var vm = this;
    this.options.slice(0).unshift({id: '', text: 'Seleccione...'});
    $(this.$el).select2({data: this.options})
      .val(this.value)
      .trigger('change')
      .on('change', function() {
         vm.$emit('input', this.value)
      });
  },
  /**
   * Monitorea el valor de un select y carga los datos del select dependiente cuando este cambia su valor
   *
   * @author Ing. Roldan Vargas <rvargas@cenditel.gob.ve> | <roldandvg@gmail.com>
   * @type {Object}
   */
  watch: {
    value: function(value) {
      $(this.$el).val(value).trigger('change');
    },
    options: function(options) {
      try {
        options.slice(0).unshift({id: '', text: 'Seleccione...'});
        $(this.$el).empty().trigger('change').select2({data: options});
        //$(".select2").find('option').attr('data-toggle', 'tooltip');
      }
      catch(err) {}
    }
  },
  destroyed: function() {
    $(this.$el).off().select2('destroy');
  },
  template: `
  <select class="form-control select2" data-toggle="tooltip" title="Seleccione una opción">
    <slot></slot>
  </select>
  `
});

Vue.component('family-group', {
  props: {
    family_group_id: Number,
  },
  data() {
    return {
      record: {
        id: '',
        username: '',
        email: '',
        building_id: '',
        department_id: '',
        departmentId: '',
        people: [],
      },
      vote_types: [],
      relationships: [],
      buildings: [],
      departments: [],
      genders: [],
      url: 'user/family-group/save',
      errors: {
        family_group: {
          username: [],
          email: [],
          building_id: [],
          department_id: [],
        },
        people: [],
      },
    }
  },

  created() {
    const vm = this;
    vm.getVoteTypes();
    vm.getRelationships();
    vm.getBuildings();
    vm.getDepartments();
    vm.getGenders();
  },

  methods: {
    /**
     * Método que permite reiniciar los datos del modelo record
     *
     * @author  William Páez <paez.william8@gmail.com>
     */
    reset() {
      this.record = {
        id: '',
        username: '',
        email: '',
        building_id: '',
        department_id: '',
        people: [],
      }
    },

    /**
     * Método que permite agregar personas dinamicamente
     *
     * @author  William Páez <paez.william8@gmail.com>
     */
    addPeople() {
      const vm = this;
      vm.errors.people.push({
        first_name: [],
        last_name: [],
        id_number: [],
        email: [],
        phone: [],
        birthdate: [],
        gender_id: [],
        vote_type_id: [],
        relationship_id: [],
      });
      vm.record.people.push({
        first_name: '',
        last_name: '',
        has_id_number: 'y',
        id_number: '',
        email: '',
        phone: '',
        birthdate: '',
        gender_id: '',
        vote_type_id: '',
        relationship_id: '',
        family_head: false,
      });
    },

    /**
     * Método que permite eliminar personas dinamicamente
     *
     * @author  William Páez <paez.william8@gmail.com>
     */
    deletePerson(index, el) {
      const vm = this;
      if( typeof(el[index].id) != 'undefined' ) {
        axios.get(`/user/person/delete/${el[index].id}/`).then(response => {
          el.splice(index, 1);
          vm.errors.people.pop();
        });
      }
      else {
        el.splice(index, 1);
        vm.errors.people.pop();
      }
    },

    /**
     * Método que permite agregar amonestaciones
     *
     * @author  William Páez <paez.william8@gmail.com>
     */
    addAdmonition() {
      const vm = this;      
    },

    /**
     * Método que permite eliminar amonestaciones dinamicamente
     *
     * @author  William Páez <paez.william8@gmail.com>
     */
    deleteAdmonition(index, el) {
      const vm = this;
    },

    /**
     * Método que obtiene los datos de un grupo familiar
     *
     * @author  William Páez <paez.william8@gmail.com>
     */
    getFamilyGroup() {
      const vm = this;
      axios.get(`/user/family-group/detail/${vm.family_group_id}/`).then(response => {
        vm.record = response.data.record;
        vm.record.building_id = response.data.record.building_id;
        vm.record.departmentId = response.data.record.department_id;
        for (var index in vm.record.people) {
          vm.errors.people.push({
            first_name: [],
            last_name: [],
            id_number: [],
            email: [],
            phone: [],
            birthdate: [],
            gender_id: [],
            vote_type_id: [],
            relationship_id: [],
          });
        }
      });
    },
  },

  mounted() {
    const vm = this;
    if(vm.family_group_id) {
      vm.getFamilyGroup();
      vm.url = 'user/family-group/update';
    }
  },

  template: `
    <!-- card - BEGIN -->
    <div class="card">
      <div class="card-header">
        Registrar
      </div>
      <div class="card-body">
        <div class="container">
          <div class="row">
            <div class="col-sm">
              <div class="form-group">
                <label class="col-sm control-label" for="id_username">
                  Usuario: <i class="fa fa-asterisk item-required" aria-hidden="true"></i>
                </label>
                <div class="col-sm">
                  <div class="form-inline">
                    <input type="text" class="form-control input-sm" data-toggle="tooltip" title="Indique el nombre de usuario" v-model="record.username">
                    <input type="hidden" v-model="record.id">
                  </div>
                </div>
              </div>
              <div v-if="errors.family_group.username">
                <div class="alert alert-danger" v-if="errors.family_group.username.length > 0">
                  <ul>
                    <li v-for="error in errors.family_group.username">{{ error }}</li>
                  </ul>
                </div>
              </div>
            </div>
            <div class="col-sm">
              <div class="form-group ">
                <label class="col-sm control-label" for="id_email">
                  Correo Electrónico: <i class="fa fa-asterisk item-required" aria-hidden="true"></i>
                </label>
                <div class="col-sm">
                  <div class="form-inline">
                    <input type="email" class="form-control input-sm" data-toggle="tooltip" title="Indique el correo electrónico" v-model="record.email">
                  </div>
                </div>
              </div>
              <div v-if="errors.family_group.email">
                <div class="alert alert-danger" v-if="errors.family_group.email.length > 0">
                  <ul>
                    <li v-for="error in errors.family_group.email">{{ error }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-sm">
              <div class="form-group">
                <label class="col-sm control-label" for="id_building">
                  Edificio:
                </label>
                <div class="col-sm">
                  <div class="form-inline">
                    <select2
                      :options="buildings"
                      @input="$event = getDepartments()"
                      v-model="record.building_id">
                    </select2>
                    <i class="fa fa-asterisk item-required" aria-hidden="true"></i>
                  </div>
                </div>
              </div>
              <div v-if="errors.family_group.building_id">
                <div class="alert alert-danger" v-if="errors.family_group.building_id.length > 0">
                  <ul>
                    <li v-for="error in errors.family_group.building_id">{{ error }}</li>
                  </ul>
                </div>
              </div>
            </div>
            <div class="col-sm">
              <div class="form-group">
                <label class="col-sm control-label" for="id_department">
                  Departamento:
                </label>
                <div class="col-sm">
                  <div class="form-inline">
                    <select2 :options="departments"
                      v-model="record.department_id">
                    </select2>
                    <i class="fa fa-asterisk item-required" aria-hidden="true"></i>
                  </div>
                </div>
              </div>
              <div v-if="errors.family_group.department_id">
                <div class="alert alert-danger" v-if="errors.family_group.department_id.length > 0">
                  <ul>
                    <li v-for="error in errors.family_group.department_id">{{ error }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <hr>
      <div class="card-body">
        <div class="container">
          <div class="row" v-if="errors.general_error">
            <div class="col-sm alert alert-danger" v-if="errors.general_error.length > 0">
              <ul>
                <li v-for="error in errors.general_error">{{ error }}</li>
              </ul>
            </div>
          </div>
          <div class="row">
            <div class="col-sm">
              <h6>
                Agregar Integrantes <i class="fa fa-plus-circle" @click="addPeople"></i>
              </h6>
            </div>
          </div>

          <div v-for="(person, index) in record.people">
            <div class="row">
              <div class="col-sm">
                <div class="form-group ">
                  <label class="control-label" for="">
                    Nombres:
                  </label>
                  <input type="text" class="form-control input-sm" data-toggle="tooltip" title="Indique los nombres" v-model="person.first_name">
                </div>
                <div v-if="errors.people[index].first_name">
                  <div class="alert alert-danger" v-if="errors.people[index].first_name.length > 0">
                    <ul>
                      <li v-for="error in errors.people[index].first_name">{{ error }}</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div class="col-sm">
                <div class="form-group ">
                  <label class="control-label" for="">
                    Apellidos:
                  </label>
                  <input type="text" class="form-control input-sm" data-toggle="tooltip" title="Indique los apellidos" v-model="person.last_name">
                </div>
                <div v-if="errors.people[index].last_name">
                  <div class="alert alert-danger" v-if="errors.people[index].last_name.length > 0">
                    <ul>
                      <li v-for="error in errors.people[index].last_name">{{ error }}</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div class="col-sm">
                <div class="form-inline">
                  <div class="form-group">
                    <select class="select2" title="¿Tiene cédula de identidad?" v-model="person.has_id_number">
                      <option value="y">Si</option>
                      <option value="n">No</option>
                    </select>
                  </div>
                  <div class="form-group" v-show="person.has_id_number=='y'">
                    <input type="text" class="form-control input-sm" data-toggle="tooltip" title="Indique la cédula de identidad" placeholder="Cédula de Identidad" v-model="person.id_number">
                  </div>
                  <div v-if="errors.people[index].id_number">
                    <div class="alert alert-danger" v-if="errors.people[index].id_number.length > 0">
                      <ul>
                        <li v-for="error in errors.people[index].id_number">{{ error }}</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-sm">
                <div class="form-group ">
                  <label class="control-label" for="">
                    Correo Electrónico:
                  </label>
                  <input type="email" class="form-control input-sm" data-toggle="tooltip" title="Indique el correo electrónico" v-model="person.email">
                </div>
                <div v-if="errors.people[index].email">
                  <div class="alert alert-danger" v-if="errors.people[index].email.length > 0">
                    <ul>
                      <li v-for="error in errors.people[index].email">{{ error }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <div class="row">
              <div class="col-sm">
                <div class="form-group ">
                  <label class="control-label" for="">
                    Número Telefónico:
                  </label>
                  <input type="text" class="form-control input-sm" data-toggle="tooltip" title="Indique el número telefónico" v-model="person.phone">
                </div>
                <div v-if="errors.people[index].phone">
                  <div class="alert alert-danger" v-if="errors.people[index].phone.length > 0">
                    <ul>
                      <li v-for="error in errors.people[index].phone">{{ error }}</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div class="col-sm">
                <div class="form-group ">
                  <label class="control-label" for="">
                    Fecha de Nacimiento:
                  </label>
                  <input type="date" class="form-control input-sm" data-toggle="tooltip" title="Indique la fecha de nacimiento" v-model="person.birthdate">
                </div>
                <div v-if="errors.people[index].birthdate">
                  <div class="alert alert-danger" v-if="errors.people[index].birthdate.length > 0">
                    <ul>
                      <li v-for="error in errors.people[index].birthdate">{{ error }}</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div class="col-sm">
                <div class="form-group ">
                  <label class="control-label" for="">
                    Género:
                  </label>
                  <select2
                    :options="genders"
                    v-model="person.gender_id">
                  </select2>
                </div>
                <div v-if="errors.people[index].gender_id">
                  <div class="alert alert-danger" v-if="errors.people[index].gender_id.length > 0">
                    <ul>
                      <li v-for="error in errors.people[index].gender_id">{{ error }}</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div class="col-sm">
                <div class="form-group ">
                  <label class="control-label" for="">
                    Tipo de Voto:
                  </label>
                  <select2
                    :options="vote_types"
                    v-model="person.vote_type_id">
                  </select2>
                </div>
                <div v-if="errors.people[index].vote_type_id">
                  <div class="alert alert-danger" v-if="errors.people[index].vote_type_id.length > 0">
                    <ul>
                      <li v-for="error in errors.people[index].vote_type_id">{{ error }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <div class="row">
              <div class="col-sm">
                <div class="form-group ">
                  <label class="control-label" for="">
                    Parentesco:
                  </label>
                  <select2
                    :options="relationships"
                    v-model="person.relationship_id">
                  </select2>
                </div>
                <div v-if="errors.people[index].relationship_id">
                  <div class="alert alert-danger" v-if="errors.people[index].relationship_id.length > 0">
                    <ul>
                      <li v-for="error in errors.people[index].relationship_id">{{ error }}</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div class="col-sm">
                <div class="form-group">
                  <label class="control-label" for="">
                    ¿Jefe Familiar?
                  </label>
                  <input type="checkbox" v-model="person.family_head">
                </div>
              </div>
              <div class="col-sm">
                <div class="form-group">
                  <button class="btn btn-sm btn-danger btn-action" type="button"
                    @click="deletePerson(index, record.people)"
                    title="Eliminar este dato" data-toggle="tooltip" data-placement="right">
                    <i class="fa fa-minus-circle"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="card-footer small text-right">
        <button type="button" class="btn btn-primary btn-sm" data-toggle="tooltip" @click="reset">Limpiar</button>
        <button type="submit" class="btn btn-primary btn-sm" data-toggle="tooltip" @click="createRecord(url)">Registrar</button>
      </div>
    </div>
    <!-- card - END -->
  `
});

Vue.component('search', {
  data() {
    return {
      id_number: '',
      record: [],
      errors: '',
    }
  },

  methods: {
    /**
     * Método que obtiene los datos de una persona
     *
     * @author  William Páez <paez.william8@gmail.com>
     */
    getPerson() {
      const vm = this;
      if( vm.id_number != '' ) {
        axios.get(`/user/searches/${vm.id_number}/`).then(response => {
          vm.record = response.data.record;
          vm.errors = response.data.error;
        });
      }
    }
  },

  template: `
    <!-- card - BEGIN -->
    <div class="card">
      <div class="card-header">
        Búsqueda por cédula de identidad
      </div>

      <!-- card body - BEGIN -->
      <div class="card-body">
        <div class="container">
          <!-- row - BEGIN -->
          <div class="row">
            <div class="col-sm-6">
              <div class="form-group">
                <input
                  type="text" class="form-control input-sm"
                  data-toggle="tooltip"
                  title="Indique el texto de búsqueda"
                  placeholder="Buscar..."
                  v-model="id_number"
                >
              </div>
              <div v-show="errors">
                <div class="alert alert-danger">
                  <ul>
                    <li>{{ errors }}</li>
                  </ul>
                </div>
              </div>
            </div>
            <div class="col-sm-2">
              <div class="form-group">
                <button class="btn btn-sm btn-primary btn-action" type="button"
                  @click="getPerson()"
                  title="Buscar un dato" data-toggle="tooltip" data-placement="right">
                  <i class="fas fa-fw fa-search"></i>
                </button>
              </div>
            </div>
          </div>
          <!-- row - END -->

          <!-- row - BEGIN -->
          <div class="row">
            <div class="col-sm-6">
              <div class="form-group font-weight-bold">
                Datos del Usuario Grupo Familiar
              </div>
            </div>
          </div>
          <!-- row - END -->

          <!-- row - BEGIN -->
          <div class="row">
            <div class="col-sm">
              <div class="form-group">
                <label class="col-sm control-label font-weight-bold">
                  Usuario
                </label>
                <div class="col-sm">
                  <div class="form-inline">
                    {{ record.username }}
                  </div>
                </div>
              </div>
            </div>
            <div class="col-sm">
              <div class="form-group">
                <label class="col-sm control-label font-weight-bold">
                  Correo Electrónico
                </label>
                <div class="col-sm">
                  <div class="form-inline">
                    {{ record.email }}
                  </div>
                </div>
              </div>
            </div>
            <div class="col-sm">
              <div class="form-group">
                <label class="col-sm control-label font-weight-bold">
                  Departamento
                </label>
                <div class="col-sm">
                  <div class="form-inline">
                    {{ record.department }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <!-- row - END -->

          <!-- row - BEGIN -->
          <div class="row">
            <div class="col-sm-6">
              <div class="form-group font-weight-bold">
                Integrantes del Grupo Familiar
              </div>
            </div>
          </div>
          <!-- row - END -->

          <div v-for="(person, index) in record.people">
            <hr>
            <!-- row - BEGIN -->
            <div class="row" :class="{'text-info' : person.family_head }">
              <div class="col-sm">
                <div class="form-group">
                  <label class="col-sm control-label font-weight-bold">
                    Nombres y Apellidos
                  </label>
                  <div class="col-sm">
                    <div class="form-inline">
                      {{ person.first_name }} {{ person.last_name }}&nbsp;<span v-show="person.family_head"> - Jefe familiar </span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-sm" :class="{'text-success' : id_number==person.id_number }">
                <div class="form-group">
                  <label class="col-sm control-label font-weight-bold">
                    Cédula de Identidad
                  </label>
                  <div class="col-sm">
                    <div class="form-inline">
                      {{ person.id_number }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-sm">
                <div class="form-group">
                  <label class="col-sm control-label font-weight-bold">
                    Correo Electrónico
                  </label>
                  <div class="col-sm">
                    <div class="form-inline">
                      {{ person.email }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-sm">
                <div class="form-group">
                  <label class="col-sm control-label font-weight-bold">
                    Número Telefónico
                  </label>
                  <div class="col-sm">
                    <div class="form-inline">
                      {{ person.phone }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!-- row - END -->

            <!-- row - BEGIN -->
            <div class="row" :class="{'text-info' : person.family_head }">
              <div class="col-sm">
                <div class="form-group">
                  <label class="col-sm control-label font-weight-bold">
                    Fecha de Nacimiento
                  </label>
                  <div class="col-sm">
                    <div class="form-inline">
                      {{ person.birthdate }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-sm">
                <div class="form-group">
                  <label class="col-sm control-label font-weight-bold">
                    Género
                  </label>
                  <div class="col-sm">
                    <div class="form-inline">
                      {{ person.gender }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-sm">
                <div class="form-group">
                  <label class="col-sm control-label font-weight-bold">
                    Tipo de Voto
                  </label>
                  <div class="col-sm">
                    <div class="form-inline">
                      {{ person.vote_type }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-sm">
                <div class="form-group">
                  <label class="col-sm control-label font-weight-bold">
                    Parentesco
                  </label>
                  <div class="col-sm">
                    <div class="form-inline">
                      {{ person.relationship }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!-- row - END -->

            <!-- row - BEGIN -->
            <div class="row" :class="{'text-info' : person.family_head }">
              <div class="col-sm">
                <div class="form-group">
                  <label class="col-sm control-label font-weight-bold">
                    Edad
                  </label>
                  <div class="col-sm">
                    <div class="form-inline">
                      {{ person.age }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!-- row - END -->
          </div>
        </div>
      </div>
      <!-- card body - END -->

    </div>
    <!-- card - END -->
  `
});

Vue.component('search-for-age', {
  data() {
    return {
      age: '',
      record: [],
    }
  },

  methods: {
    /**
     * Método que obtiene los datos de personas por edad
     *
     * @author  William Páez <paez.william8@gmail.com>
     */
    getPersonAge() {
      const vm = this;
      if( vm.age != '' ) {
        axios.get(`/user/searches-for-age/${vm.age}/`).then(response => {
          vm.record = response.data.record;
        });
      }
    }
  },

  template: `
    <!-- card - BEGIN -->
    <div class="card">
      <div class="card-header">
        Búsqueda por edad
      </div>

      <!-- card body - BEGIN -->
      <div class="card-body">
        <!-- container - BEGIN -->
        <div class="container">
          <!-- row - BEGIN -->
          <div class="row">
            <div class="col-sm-6">
              <div class="form-group">
                <input
                  type="number"
                  min="0"
                  class="form-control input-sm"
                  data-toggle="tooltip"
                  title="Indique la edad"
                  placeholder="Buscar..."
                  v-model="age"
                >
              </div>
            </div>
            <div class="col-sm-2">
              <div class="form-group">
                <button class="btn btn-sm btn-primary btn-action" type="button"
                  @click="getPersonAge()"
                  title="Buscar un dato" data-toggle="tooltip" data-placement="right">
                  <i class="fas fa-fw fa-search"></i>
                </button>
              </div>
            </div>
          </div>
          <!-- row - END -->

          <!-- row - BEGIN -->
          <div class="row">
            <div class="col-sm">
              <div class="form-group">
                <label class="col-sm control-label font-weight-bold">
                  Total
                </label>
                <div class="col-sm">
                  <div class="form-inline">
                    {{ record.total_children }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <!-- row - END -->

          <div class="table-responsive">
            <table class="table table-striped table-hover table-bordered display dataTable" style="width:100%;">
              <thead>
                <tr>
                  <th>Nombres y Apellidos</th>
                  <th>Cédula de Identidad</th>
                  <th>Fecha de nacimiento</th>
                  <th>Género</th>
                  <th>Edad</th>
                  <th>Departamento</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(person, index) in record.people">
                  <td>{{ person.first_name }} {{ person.last_name }}</td>
                  <td>{{ person.id_number }}</td>
                  <td>{{ person.birthdate }}</td>
                  <td>{{ person.gender }}</td>
                  <td>{{ person.age }}</td>
                  <td>{{ person.department }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <!-- container - END -->
      </div>
      <!-- card body - END -->
    </div>
    <!-- card - END -->
  `
});

Vue.component('age', {
  data() {
    return {
      age1: '',
      age2: '',
      record: [],
      errors: '',
    }
  },

  template: `
    <!-- card - BEGIN -->
    <div class="card">
      <div class="card-header">
        Filtrar entre rango de edades
      </div>

      <!-- card body - BEGIN -->
      <div class="card-body">
        <div class="container">
          <!-- row - BEGIN -->
          <div class="row">
            <div class="col-sm-6">
              <div class="form-group">
                <input
                  type="number"
                  min="0"
                  class="form-control input-sm"
                  data-toggle="tooltip"
                  title="Indique la edad"
                  placeholder="Buscar..."
                  v-model="age1"
                >
              </div>
              <div v-show="errors">
                <div class="alert alert-danger">
                  <ul>
                    <li>{{ errors }}</li>
                  </ul>
                </div>
              </div>
            </div>
            <div class="col-sm-6">
              <div class="form-group">
                <input
                  type="number"
                  min="0"
                  class="form-control input-sm"
                  data-toggle="tooltip"
                  title="Indique la edad"
                  placeholder="Buscar..."
                  v-model="age2"
                >
              </div>
              <div v-show="errors">
                <div class="alert alert-danger">
                  <ul>
                    <li>{{ errors }}</li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="col-sm-6">
              <div class="form-group">
                <a :href="'/filtros/edad/?age1=' + age1 + '&age2=' + age2" target="_blank"> Descargar por Edades </a>
              </div>
            </div>
          </div>
          <!-- row - END -->
        </div>
      </div>
      <!-- card body - END -->

    </div>
    <!-- card - END -->
  `
});
