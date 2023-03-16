/**
 * Opciones de configuración global para utilizar en todos los componentes vuejs de la aplicación
 *
 * @author  William Páez <paez.william8@gmail.com>
 * @param  {object} methods Métodos generales a implementar en CRUDS
 */
Vue.mixin({  
  props: {
    route_list: {
      type: String,
      required: false,
      default: ''
    },
    route_create: {
      type: String,
      required: false,
      default: ''
    },
    route_edit: {
      type: String,
      required: false,
      default: ''
    },
    route_update: {
      type: String,
      required: false,
      default: ''
    },
    route_delete: {
      type: String,
      required: false,
      default: ''
    },
    route_show: {
      type: String,
      required: false,
      default: ''
    },
  },
  methods: {
    /**
     * Método que permite eliminar una fila de campos dinamicamente
     *
     * @author  William Páez <paez.william8@gmail.com>
     */
    removeRow(index, el) {
        el.splice(index, 1);
    },

    /**
     * Método que permite crear o actualizar un registro
     *
     * @author  William Páez <paez.william8@gmail.com>
     * @author  Ing. Roldan Vargas <roldandvg@gmail.com>
     * @param  {string} url Ruta de la acción a ejecutar para la creación o actualización de datos
     */
    createRecord(url) {
      const vm = this;
      if (vm.record.id) {
        vm.updateRecord(url);
      }
      else {
        var fields = {};
        for (var index in vm.record) {
          fields[index] = vm.record[index];
        }
        axios.post('/' + url + '/', fields).then(response => {
          if (typeof(response.data.redirect) !== "undefined") {
            location.href = response.data.redirect;
          }
          else {
            vm.reset();
            vm.readRecords(url);
            //vm.showMessage('store');
          }
        }).catch(error => {
          vm.errors = {
            family_group: {
              username: [],
              email: [],
              building_id: [],
              department_id: [],
            },
            people: [{}],
          };
          if (typeof(error.response) != "undefined") {
            for (var index in error.response.data.errors) {
              if (error.response.data.errors[index]) {
                vm.errors[index] = error.response.data.errors[index];
              }
            }
          }
        });
      }
    },

    /**
     * Método que permite actualizar información
     *
     * @author  William Páez <paez.william8@gmail.com>
     * @author  Ing. Roldan Vargas <roldandvg@gmail.com>
     * @param  {string} url Ruta de la acción que modificará los datos
     */
    updateRecord(url) {
      const vm = this;
      var fields = {};
      for (var index in vm.record) {
        fields[index] = vm.record[index];
      }
      axios.put('/' + url + '/' + vm.record.id + '/', fields).then(response => {
        if (typeof(response.data.redirect) !== "undefined") {
          location.href = response.data.redirect;
        }
        else {
          vm.readRecords(url);
          vm.reset();
          //vm.showMessage('update');
        }
      }).catch(error => {
        vm.errors = {
          family_group: {
            username: [],
            email: [],
            building_id: [],
            department_id: [],
          },
          people: [{}],
        };
        if (typeof(error.response) != "undefined") {
          for (var index in error.response.data.errors) {
            if (error.response.data.errors[index]) {
              //vm.errors.push(error.response.data.errors[index][0]);
              vm.errors[index] = error.response.data.errors[index];
            }
          }
        }
      });
    },

    getVoteTypes() {
      const vm = this;
      vm.vote_types = [];
      axios.get('/vote-types/list/').then(response => {
        vm.vote_types = response.data.list;
      });
    },

    getRelationships() {
      const vm = this;
      vm.vote_types = [];
      axios.get('/relationships/list/').then(response => {
        vm.relationships = response.data.list;
      });
    },

    getBuildings() {
      const vm = this;
      vm.buildings = [];
      axios.get('/buildings/list/').then(response => {
        vm.buildings = response.data.list;
      });
    },

    async getDepartments() {
      const vm = this;
      vm.departments = [];
      if (vm.record.building_id) {
        await axios.get(`/get-departments/${vm.record.building_id}`).then(response => {
          vm.departments = response.data.list;
        });
        if (vm.record.departmentId) {
          vm.record.department_id = vm.record.departmentId;
        }
      }
    },
  }
});
