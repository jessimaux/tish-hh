<template>
  <div v-if="profileStore.data" class="profile-wrapper">
    <div class="row">
      <div class="col-lg-2">
        <div class="d-flex align-items-start">
          <div class="nav flex-column nav-pills me-3" id="v-pills-tab" role="tablist" aria-orientation="vertical">
            <button
              class="nav-link active"
              id="v-pills-profile-tab"
              data-bs-toggle="pill"
              data-bs-target="#v-pills-profile"
              type="button"
              role="tab"
              aria-controls="v-pills-profile"
              aria-selected="true">
              Profile
            </button>
            <button
              class="nav-link"
              id="v-pills-password-tab"
              data-bs-toggle="pill"
              data-bs-target="#v-pills-password"
              type="button"
              role="tab"
              aria-controls="v-pills-password"
              aria-selected="false">
              Password
            </button>
          </div>
        </div>
      </div>
      <div class="col-lg-10">
        <div class="tab-content" id="v-pills-tabContent">
          <div
            class="tab-pane fade show active"
            id="v-pills-profile"
            role="tabpanel"
            aria-labelledby="v-pills-profile-tab">
            <form @submit.prevent="onSubmit">
              <div class="mb-3 row">
                <label for="Email" class="col-lg-2 col-form-label">Email</label>
                <div class="col-lg-10">
                  <input type="text" class="form-control" v-model="profileStore.data.email" />
                </div>
              </div>

              <div class="mb-3 row">
                <label for="Phone" class="col-lg-2 col-form-label">Phone</label>
                <div class="col-lg-6">
                  <input type="text" class="form-control" v-model="profileStore.data.phone" />
                </div>
              </div>

              <div class="mb-3 row">
                <label for="Username" class="col-lg-2 col-form-label">Username</label>
                <div class="col-lg-10">
                  <input type="text" class="form-control" v-model="profileStore.data.username" />
                  <div class="form-text">Your shortly identificator.</div>
                </div>
              </div>

              <div class="mb-3 row">
                <label for="Name" class="col-lg-2 col-form-label">Name</label>
                <div class="col-lg-10">
                  <input type="text" class="form-control" v-model="profileStore.data.name" />
                  <div class="form-text">Set name also can help to find you by other.</div>
                </div>
              </div>

              <div class="mb-3 row">
                <label for="Bio" class="col-lg-2 col-form-label">Bio</label>
                <div class="col-lg-10">
                  <textarea
                    class="form-control"
                    rows="3"
                    style="resize: none"
                    v-model="profileStore.data.bio"></textarea>
                </div>
              </div>

              <div class="mb-3 row">
                <label for="Age" class="col-lg-2 col-form-label">Age</label>
                <div class="col-lg-2">
                  <input type="number" class="form-control" min="0" v-model="profileStore.data.age" />
                </div>
              </div>

              <div class="mb-3 row">
                <label for="Gender" class="col-lg-2 col-form-label">Gender</label>
                <div class="col-lg-3">
                  <select class="form-select" aria-label="Default select example" v-model="profileStore.data.gender">
                    <option selected></option>
                    <option value="true">Male</option>
                    <option value="false">Female</option>
                  </select>
                </div>
              </div>

              <div class="mb-3 row">
                <label for="Country" class="col-lg-2 col-form-label">Country</label>
                <div class="col-lg-10">
                  <input type="text" class="form-control" v-model="profileStore.data.country" />
                </div>
              </div>

              <div class="mb-3 row">
                <label for="Region" class="col-lg-2 col-form-label">Region</label>
                <div class="col-lg-10">
                  <input type="text" class="form-control" v-model="profileStore.data.region" />
                </div>
              </div>

              <div class="mb-3 row">
                <label for="City" class="col-lg-2 col-form-label">City</label>
                <div class="col-lg-10">
                  <input type="text" class="form-control" v-model="profileStore.data.city" />
                </div>
              </div>

              <!-- TODO: add links -->

              <button type="submit" class="btn btn-tish float-end">Save</button>
            </form>
          </div>
          <div class="tab-pane fade" id="v-pills-password" role="tabpanel" aria-labelledby="v-pills-password-tab">
            PasswordEditComponent
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useProfileStore } from '@/stores/profile'

const profileStore = useProfileStore()
profileStore.getCurrentUser()

async function onSubmit() {
  await profileStore.updateCurrentUser(profileStore.data)
}
</script>
