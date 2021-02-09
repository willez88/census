/**
 * Opciones de configuración global para utilizar en todos los componentes vuejs de la aplicación
 *
 * @author  William Páez <paez.william8@gmail.com>
 * @param  {object} methods Métodos generales a implementar en CRUDS
 */
Vue.mixin({
  data() {
    return {
      /**
       * Opciones generales a implementar en tablas
       * @type {JSON}
       */
      table_options: {
        pagination: { edge: true },
        //filterByColumn: true,
        highlightMatches: true,
        texts: {
          filter: "Buscar:",
          filterBy: 'Buscar por {column}',
          //count:'Página {page}',
          count: ' ',
          first: 'PRIMERO',
          last: 'ÚLTIMO',
          limit: 'Registros',
          //page: 'Página:',
          noResults: 'No existen registros',
          filterPlaceholder: '...',
        },
        sortIcon: {
          is: 'fa-sort cursor-pointer',
          base: 'fa',
          up: 'fa-sort-up cursor-pointer',
          down: 'fa-sort-down cursor-pointer'
        },
      },
    }
  },
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
      if (this.record.id) {
        this.updateRecord(url);
      }
      else {
        var fields = {};
        for (var index in this.record) {
          fields[index] = this.record[index];
        }
        axios.post('/' + url, fields).then(response => {
          if (typeof(response.data.redirect) !== "undefined") {
            location.href = response.data.redirect;
          }
          else {
            vm.reset();
            vm.readRecords(url);
            //vm.showMessage('store');
          }
        }).catch(error => {
          vm.errors = [];

          if (typeof(error.response) !="undefined") {
            for (var index in error.response.data.errors) {
              if (error.response.data.errors[index]) {
                vm.errors.push(error.response.data.errors[index][0]);
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
      for (var index in this.record) {
        fields[index] = this.record[index];
      }
      axios.put('/' + url + '/' + this.record.id + '/', fields).then(response => {
        if (typeof(response.data.redirect) !== "undefined") {
          location.href = response.data.redirect;
        }
        else {
          vm.readRecords(url);
          vm.reset();
          vm.showMessage('update');
        }
      }).catch(error => {
        vm.errors = [];

        if (typeof(error.response) !="undefined") {
          for (var index in error.response.data.errors) {
            if (error.response.data.errors[index]) {
              vm.errors.push(error.response.data.errors[index][0]);
            }
          }
        }
      });
    },

    getVoteTypes() {
      this.vote_types = [];
      axios.get('/vote-types/list/').then(response => {
        this.vote_types = response.data.list;
      });
    },

    getRelationships() {
      this.vote_types = [];
      axios.get('/relationships/list/').then(response => {
        this.relationships = response.data.list;
      });
    }
  }
});
